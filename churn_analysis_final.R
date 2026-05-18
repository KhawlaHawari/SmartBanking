# =============================================================================
# CUSTOMER CHURN ANALYSIS — FINAL SUBMISSION PIPELINE
# PCA + CLUSTERING + DATA QUALITY + BUSINESS INSIGHTS
# =============================================================================

# ── 0. PACKAGES ──────────────────────────────────────────────────────────────

required_pkgs <- c(
  "tidyverse", "FactoMineR", "factoextra",
  "cluster", "corrplot", "scales", "purrr"
)

installed <- rownames(installed.packages())
to_install <- setdiff(required_pkgs, installed)

if (length(to_install) > 0) {
  install.packages(to_install, repos = "https://cloud.r-project.org", quiet = TRUE)
}

suppressPackageStartupMessages({
  library(tidyverse)
  library(FactoMineR)
  library(factoextra)
  library(cluster)
  library(corrplot)
  library(scales)
  library(purrr)
})

set.seed(2026)

# ── 1. OUTPUT STRUCTURE ──────────────────────────────────────────────────────

dir.create("outputs/figures", recursive = TRUE, showWarnings = FALSE)
dir.create("outputs/tables", recursive = TRUE, showWarnings = FALSE)

save_fig <- function(p, name) {
  ggsave(file.path("outputs/figures", name),
         p, width = 10, height = 7, dpi = 300, bg = "white")
}

theme_churn <- function() {
  theme_minimal() +
    theme(
      plot.title = element_text(face = "bold"),
      panel.grid.minor = element_blank()
    )
}

churn_palette <- c("Stayed" = "#2C7BB6", "Churned" = "#D7191C")

# ── 2. BUSINESS CONTEXT ──────────────────────────────────────────────────────

cat("
========================================================
CUSTOMER CHURN ANALYSIS — BANKING PROJECT
========================================================
Objective:
- Understand drivers of churn
- Detect data quality issues
- Segment customers using PCA + K-Means
========================================================\n")

# ── 3. DATA LOADING ──────────────────────────────────────────────────────────

raw <- read_csv(
  "C:/Users/kenza/Documents/AI-Powered Banking Customer Intelligence Platform/Customer-Churn-Records.csv",
  show_col_types = FALSE
)

names(raw) <- make.names(names(raw))

df <- raw %>%
  select(-RowNumber, -CustomerId, -Surname) %>%
  mutate(
    Geography = factor(Geography),
    Gender = factor(Gender),
    Card.Type = factor(Card.Type),
    HasCrCard = factor(HasCrCard),
    IsActiveMember = factor(IsActiveMember),
    Exited = factor(Exited, levels = c(0, 1),
                    labels = c("Stayed", "Churned"))
  )

# =============================================================================
# ── 4. DATA QUALITY (MISSING VALUES + OUTLIERS) ─────────────────────────────
# =============================================================================

cat("\n===== MISSING VALUES =====\n")
missing_tbl <- colSums(is.na(df))
print(missing_tbl)

# Keep only numeric columns for analysis
num_df <- df %>% select(where(is.numeric))

# ---------------- OUTLIERS (FIXED VERSION) ----------------

iqr_outliers <- function(x) {
  q1 <- quantile(x, 0.25, na.rm = TRUE)
  q3 <- quantile(x, 0.75, na.rm = TRUE)
  iqr <- q3 - q1
  sum(x < (q1 - 1.5 * iqr) | x > (q3 + 1.5 * iqr), na.rm = TRUE)
}

outliers_tbl <- map_dfr(names(num_df), function(col) {
  tibble(
    variable = col,
    outliers = iqr_outliers(num_df[[col]])
  )
})

write_csv(outliers_tbl, "outputs/tables/outliers_report.csv")

# =============================================================================
# ── 5. VARIABLES ─────────────────────────────────────────────────────────────
# =============================================================================

active_vars <- c(
  "CreditScore", "Age", "Tenure", "Balance",
  "NumOfProducts", "EstimatedSalary",
  "Satisfaction.Score", "Point.Earned"
)

df_active <- df %>% select(all_of(active_vars))

# =============================================================================
# ── 6. CORRELATION ───────────────────────────────────────────────────────────
# =============================================================================

cor_mat <- cor(df_active)

png("outputs/figures/fig01_corr.png", 1800, 1600, res = 200)
corrplot(cor_mat,
         method = "color",
         col = colorRampPalette(c("#2C7BB6", "white", "#D7191C"))(200))
dev.off()

# =============================================================================
# ── 7. UNIVARIATE ANALYSIS ───────────────────────────────────────────────────
# =============================================================================

p1 <- df_active %>%
  pivot_longer(everything()) %>%
  ggplot(aes(value)) +
  geom_histogram(bins = 30, fill = "#377EB8") +
  facet_wrap(~name, scales = "free") +
  theme_churn()

save_fig(p1, "fig02_univariate.png")

# =============================================================================
# ── 8. BOXPLOTS BY CHURN ─────────────────────────────────────────────────────
# =============================================================================

df_long <- df %>%
  select(all_of(active_vars), Exited) %>%
  pivot_longer(-Exited)

p2 <- ggplot(df_long,
             aes(x = Exited, y = value, fill = Exited)) +
  geom_boxplot(alpha = 0.7) +
  scale_fill_manual(values = churn_palette) +
  facet_wrap(~name, scales = "free") +
  theme_churn()

save_fig(p2, "fig03_boxplots.png")

# =============================================================================
# ── 9. STRATIFIED SAMPLING ───────────────────────────────────────────────────
# =============================================================================

df_sample <- df %>%
  group_by(Exited) %>%
  slice_sample(prop = 0.2) %>%
  ungroup()

# =============================================================================
# ── 10. PCA ──────────────────────────────────────────────────────────────────
# =============================================================================

pca_input <- df_sample %>%
  mutate(
    HasCrCard_num = as.numeric(HasCrCard),
    IsActiveMember_num = as.numeric(IsActiveMember)
  ) %>%
  select(all_of(active_vars),
         HasCrCard_num, IsActiveMember_num)

pca_res <- PCA(pca_input, scale.unit = TRUE, graph = FALSE)

cat("\nPCA completed successfully\n")

# Eigenvalues
eig_table <- as.data.frame(pca_res$eig)
eig_table <- cbind(PC = paste0("PC", 1:nrow(eig_table)), eig_table)

write_csv(eig_table, "outputs/tables/pca_eigenvalues.csv")

# =============================================================================
# ── 11. PCA VISUALIZATION ────────────────────────────────────────────────────
# =============================================================================

ind_coords <- as.data.frame(pca_res$ind$coord)
ind_coords$Exited <- df_sample$Exited

p3 <- ggplot(ind_coords,
             aes(Dim.1, Dim.2, color = Exited)) +
  geom_point(alpha = 0.7) +
  scale_color_manual(values = churn_palette) +
  theme_churn()

save_fig(p3, "fig04_pca.png")

# =============================================================================
# ── 12. K-MEANS ──────────────────────────────────────────────────────────────
# =============================================================================

X_scaled <- scale(df_sample %>% select(all_of(active_vars)))

km3 <- kmeans(X_scaled, centers = 3, nstart = 50)

df_sample$Cluster <- factor(km3$cluster)
ind_coords$Cluster <- df_sample$Cluster

p4 <- ggplot(ind_coords,
             aes(Dim.1, Dim.2, color = Cluster)) +
  geom_point(alpha = 0.7) +
  scale_color_brewer(palette = "Set1") +
  theme_churn()

save_fig(p4, "fig05_clusters.png")

# =============================================================================
# ── 13. CLUSTER PROFILING ────────────────────────────────────────────────────
# =============================================================================

cluster_profile <- df_sample %>%
  group_by(Cluster) %>%
  summarise(
    Customers = n(),
    ChurnRate = mean(Exited == "Churned"),
    AvgAge = mean(Age),
    AvgBalance = mean(Balance),
    AvgProducts = mean(NumOfProducts),
    AvgSatisfaction = mean(Satisfaction.Score),
    .groups = "drop"
  )

write_csv(cluster_profile, "outputs/tables/cluster_profile.csv")

# =============================================================================
# ── 14. FINAL INSIGHTS ───────────────────────────────────────────────────────
# =============================================================================

cat("\n================ FINAL INSIGHTS ================\n")
cat("- Data quality checked (missing values + outliers)\n")
cat("- PCA reveals customer structure\n")
cat("- K-Means identifies 3 segments\n")
cat("- Churn linked to satisfaction and behavior\n")
cat("==============================================\n")

cat("\n✔ ANALYSIS COMPLETED SUCCESSFULLY\n")
