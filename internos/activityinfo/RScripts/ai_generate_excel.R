
library("ggplot2")
opt <- options(warn = -1)
rm(list = ls())

library("jsonlite")
library("activityinfo")

myArgs <- commandArgs(trailingOnly = TRUE)

ai_username <- myArgs[1]
ai_password <- myArgs[2]
db_id <- myArgs[3]
ai_id <- myArgs[4]
main_db_id <- myArgs[5]

activityInfoLogin(ai_username, ai_password)

values <- getQuantityTable(main_db_id, db_id)
outfilname<- paste('internos/activityinfo/AIReports/', ai_id, "_ai_data.csv", sep="")
write.csv(values, outfilname, row.names=FALSE)
