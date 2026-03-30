# plot_school_demographics.R
#
# Fetch the top-ranked schools in a state and create a stacked bar chart
# showing racial/ethnic demographic breakdown by school using ggplot2.
# Saves the plot as a PNG file.
#
# Usage:
#   Rscript plot_school_demographics.R
#
# Prerequisites:
#   install.packages(c("httr", "jsonlite", "ggplot2", "tidyr", "dplyr"))
#   Set environment variables:
#     SCHOOLDIGGER_APP_ID  — your API app ID
#     SCHOOLDIGGER_APP_KEY — your API app key
#
# Get a free API key at https://developer.schooldigger.com

library(httr)
library(jsonlite)
library(ggplot2)
library(tidyr)
library(dplyr)

API_BASE <- "https://api.schooldigger.com/v2.3"

app_id  <- Sys.getenv("SCHOOLDIGGER_APP_ID")
app_key <- Sys.getenv("SCHOOLDIGGER_APP_KEY")

if (nchar(app_id) == 0 || nchar(app_key) == 0) {
  stop("Set SCHOOLDIGGER_APP_ID and SCHOOLDIGGER_APP_KEY environment variables.\n",
       "Get a free API key at https://developer.schooldigger.com")
}

state <- "WA"
level <- "Elementary"
n_schools <- 20

cat(sprintf("Fetching top %d %s schools in %s...\n", n_schools, level, state))

response <- GET(
  url   = paste0(API_BASE, "/rankings/schools/", state),
  query = list(
    level   = level,
    page    = 1,
    perPage = n_schools,
    appID   = app_id,
    appKey  = app_key
  )
)

if (http_error(response)) {
  stop(sprintf("API error %d: %s", status_code(response), content(response, "text")))
}

data <- fromJSON(content(response, "text", encoding = "UTF-8"), flatten = TRUE)
schools_raw <- data$schoolList

if (is.null(schools_raw) || length(schools_raw) == 0) {
  stop("No schools returned from rankings endpoint.")
}

# SchoolDigger year convention: year 2025 = 2024-25 school year
rank_year <- data$rankYear
year_label <- if (!is.null(rank_year)) sprintf("%d-%s", rank_year - 1, substr(rank_year, 3, 4)) else "N/A"
cat(sprintf("Rank year: %s\n\n", year_label))

# Extract demographic percentages from schoolYearlyDetails (most recent year)
# Field names match the SchoolDigger API response
get_demo <- function(yearly_list, field) {
  sapply(yearly_list, function(x) {
    if (is.null(x) || length(x) == 0) return(NA_real_)
    val <- x[[1]][[field]]
    if (is.null(val)) NA_real_ else as.numeric(val)
  })
}

yearly <- schools_raw$schoolYearlyDetails

demo_df <- data.frame(
  school_name = substr(schools_raw$schoolName, 1, 30),
  White       = get_demo(yearly, "percentofWhiteStudents"),
  Hispanic    = get_demo(yearly, "percentofHispanicStudents"),
  Black       = get_demo(yearly, "percentofAfricanAmericanStudents"),
  Asian       = get_demo(yearly, "percentofAsianStudents"),
  Two_or_More      = get_demo(yearly, "percentofTwoOrMoreRaceStudents"),
  Pacific_Islander = get_demo(yearly, "percentofPacificIslanderStudents"),
  # American Indian + any unaccounted remainder grouped as Other
  Other            = get_demo(yearly, "percentofIndianStudents"),
  stringsAsFactors = FALSE
)

# Replace NA with 0 for plotting
demo_df[is.na(demo_df)] <- 0

# Pivot to long format for ggplot2
demo_long <- demo_df %>%
  pivot_longer(
    cols      = -school_name,
    names_to  = "group",
    values_to = "percent"
  ) %>%
  mutate(group = factor(group, levels = c("White", "Hispanic", "Asian", "Black", "Two_or_More", "Pacific_Islander", "Other")))

# Order schools by their rank (they arrive in rank order)
demo_long$school_name <- factor(demo_long$school_name,
                                 levels = rev(unique(demo_long$school_name)))

cat("Building demographic chart...\n")

pal <- c(
  White            = "#4E79A7",
  Hispanic         = "#F28E2B",
  Asian            = "#59A14F",
  Black            = "#E15759",
  Two_or_More      = "#B07AA1",
  Pacific_Islander = "#76B7B2",
  Other            = "#9C755F"
)

p <- ggplot(demo_long, aes(x = school_name, y = percent, fill = group)) +
  geom_bar(stat = "identity", width = 0.75) +
  coord_flip() +
  scale_fill_manual(values = pal, name = "Group") +
  scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(0, 105)) +
  labs(
    title    = sprintf("Top %d %s Schools in %s — Demographics (%s)", n_schools, level, state, year_label),
    subtitle = "Source: SchoolDigger K-12 School Data API (developer.schooldigger.com)",
    x        = NULL,
    y        = "Percent of Students"
  ) +
  theme_minimal(base_size = 11) +
  theme(
    plot.title    = element_text(face = "bold"),
    legend.position = "bottom"
  )

outfile <- sprintf("%s_%s_demographics.png", state, level)
ggsave(outfile, p, width = 10, height = 8, dpi = 150)
cat(sprintf("Saved: %s\n", outfile))
