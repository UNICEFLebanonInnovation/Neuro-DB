
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

values <- getQuantityTable("ck2yrizmo2", database.id)
outfilname<- paste('internos/activityinfo/AIReports/', ai_id, "_ai_data.csv", sep="")
write.csv(values, outfilname, row.names=FALSE)
