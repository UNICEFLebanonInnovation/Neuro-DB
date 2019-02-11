
library("ggplot2")
opt <- options(warn = -1)
rm(list = ls())

library("jsonlite")
library("activityinfo")

myArgs <- commandArgs(trailingOnly = TRUE)

ai_username <- myArgs[1]
ai_password <- myArgs[2]
ai_id <- myArgs[3]

activityInfoLogin(ai_username, ai_password)

# Convert to numerics
database.id <- as.numeric(ai_id)

if (is.na(database.id)) {
  stop("you forgot to set the database identifier at the top of this script!")
}
values <- getDatabaseValueTable(database.id, col.names = c("Funded by" = "Funded_by", "Funded By" = "Funded_by"))
values$start_date <-strftime(values$start_date,"%Y-%m-%d")
outfilname<- paste('internos/activityinfo/AIReports/', ai_id, "_ai_data.csv", sep="")
write.csv(values, outfilname, row.names=FALSE)
