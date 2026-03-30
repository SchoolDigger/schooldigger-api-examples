# search_schools.R
#
# Search for schools using the SchoolDigger K-12 School Data API.
# Returns results as a data.frame and prints a summary.
#
# Usage:
#   Rscript search_schools.R
#
# Prerequisites:
#   install.packages(c("httr", "jsonlite"))
#   Set environment variables:
#     SCHOOLDIGGER_APP_ID  — your API app ID
#     SCHOOLDIGGER_APP_KEY — your API app key
#
# Get a free API key at https://developer.schooldigger.com

library(httr)
library(jsonlite)

API_BASE <- "https://api.schooldigger.com/v2.3"

# Read credentials from environment variables
app_id  <- Sys.getenv("SCHOOLDIGGER_APP_ID")
app_key <- Sys.getenv("SCHOOLDIGGER_APP_KEY")

if (nchar(app_id) == 0 || nchar(app_key) == 0) {
  stop("Set SCHOOLDIGGER_APP_ID and SCHOOLDIGGER_APP_KEY environment variables.\n",
       "Get a free API key at https://developer.schooldigger.com")
}

# Search parameters
state <- "WA"
query <- "Lincoln"

cat(sprintf("Searching for '%s' schools in %s...\n", query, state))

response <- GET(
  url   = paste0(API_BASE, "/schools"),
  query = list(
    st     = state,
    q      = query,
    appID  = app_id,
    appKey = app_key
  )
)

if (http_error(response)) {
  stop(sprintf("API error %d: %s", status_code(response), content(response, "text")))
}

data <- fromJSON(content(response, "text", encoding = "UTF-8"), flatten = TRUE)

if (is.null(data$schoolList) || length(data$schoolList) == 0) {
  cat("No schools found.\n")
  quit(save = "no")
}

schools_raw <- data$schoolList

# Build a clean data.frame with the most useful fields
schools <- data.frame(
  school_id   = schools_raw$schoolid,
  name        = schools_raw$schoolName,
  city        = schools_raw$address.city,
  state       = schools_raw$address.state,
  low_grade   = schools_raw$lowGrade,
  high_grade  = schools_raw$highGrade,
  district    = schools_raw$district.districtName,
  stringsAsFactors = FALSE
)

# Pull rank and enrollment from nested lists
get_first <- function(lst, key) {
  sapply(lst, function(x) {
    if (is.null(x) || length(x) == 0) return(NA)
    val <- x[[1]][[key]]
    if (is.null(val)) NA else val
  })
}

rank_history   <- schools_raw$rankHistory
yearly_details <- schools_raw$schoolYearlyDetails

schools$rank        <- get_first(rank_history,   "rank")
schools$rank_of     <- get_first(rank_history,   "rankOf")
schools$stars       <- get_first(rank_history,   "rankStars")  # 0-5 star scale
schools$students    <- get_first(yearly_details, "numberOfStudents")
schools$free_lunch_pct <- get_first(yearly_details, "percentFreeDiscLunch")

cat(sprintf("\nFound %d school(s) total. Showing first %d:\n\n",
            data$numberOfSchools, nrow(schools)))

# Print formatted summary
for (i in seq_len(nrow(schools))) {
  s <- schools[i, ]
  rank_str <- if (!is.na(s$rank)) sprintf("%d of %d", s$rank, s$rank_of) else "N/A"
  cat(sprintf(
    "%-40s %-18s Grades %-6s Rank: %-14s Stars: %s  Students: %s\n",
    substr(s$name, 1, 40),
    substr(s$city, 1, 18),
    paste0(s$low_grade, "-", s$high_grade),
    rank_str,
    ifelse(is.na(s$stars), "N/A", s$stars),
    ifelse(is.na(s$students), "N/A", s$students)
  ))
}

cat("\n--- Data Frame Summary ---\n")
print(summary(schools[, c("stars", "students", "free_lunch_pct")]))

# Return the data.frame (useful when sourcing this script)
invisible(schools)
