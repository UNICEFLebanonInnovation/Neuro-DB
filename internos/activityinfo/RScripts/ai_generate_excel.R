
library("ggplot2")
opt <- options(warn = -1)
rm(list = ls())

library("jsonlite")
library("activityinfo")
activityInfoLogin('mkarnib@unicef.org', 'ILOVEmadrid@2018')

myArgs <- commandArgs(trailingOnly = TRUE)

# Convert to numerics
database.id <- as.numeric(myArgs)

if (is.na(database.id)) {
  stop("you forgot to set the database identifier at the top of this script!")
}
#values <- getDatabaseValueTable(database.id)
values <- getDatabaseValueTable(database.id, col.names = c("Funded by" = "Funded_by"))
outfilname<- paste('internos/activityinfo/AIReports/', myArgs, "_ai_data.csv", sep="")
write.csv(values, outfilname, row.names=FALSE)
