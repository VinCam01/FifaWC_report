library(tidyverse)
library(dplyr)
library(ggplot2)

options(max.print = 200)
matches = read.csv('WorldCupMatches.csv')
players = read.csv('WorldCupPlayers.csv')
wcups = read.csv('WorldCups.csv')

print(head(matches))
print(head(players))
print(head(wcups))

cat("matches:", dim(matches), "\n")
cat("players:", dim(players), "\n")
cat("wcups:", dim(wcups), "\n")

str(matches)
str(players)
str(wcups)

print(colSums(is.na(matches)))
print(colSums(is.na(players)))
print(colSums(is.na(wcups)))

matches = na.omit(matches)
matches

summary(matches)
summary(players)
summary(wcups)

#%% GOAL SCORED FOR EACH WORLD CUP
ggplot(wcups, aes(x = Year, y = GoalsScored)) +
  geom_line() +
  geom_point() +
  scale_x_continuous(breaks = wcups$Year, labels = wcups$Year, expand = c(0, 0)) +
  scale_y_continuous(breaks = seq(70, 175, 10), expand = c(0, 0)) +
  labs(title = "Goal Scored For Each World Cup")+
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1),
        panel.grid.major = element_line(colour = "gray", linetype = "dashed"),
        panel.grid.minor = element_blank())

#%% COUNTRY THAT WON MOST WORLD CUPS
wcups$Winner = ifelse(wcups$Winner == 'Germany FR', 'Germany', wcups$Winner)
ggplot(wcups, aes(x = Winner, fill = Winner)) +
  geom_bar() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_y_continuous(breaks = seq(0, 10, 1)) +
  labs(title = "Who Won Most World Cups?") +
  scale_fill_manual(values = c("Brazil" = "gold2", "Germany" = "black", "Italy" = "green3", "Argentina" = "lightblue", 'England' = 'red', 'France' = 'blue', 'Uruguay' ='steelblue2', 'Spain' = 'red4' )) +
  theme_minimal()

#%% TREND OF ATTENDANCE
mean_attendance = matches %>%
  group_by(Year) %>%
  summarise(mean_attendance = mean(Attendance, na.rm = TRUE))

mean_attendance

rownames(mean_attendance) = NULL

ggplot(mean_attendance, aes(x = Year, y = mean_attendance)) +
  geom_point(color="black") + 
  geom_line(color="skyblue")+
  ggtitle("Trend of Attendance") +
  xlab("Year") +
  ylab("Attendance") +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  theme_minimal()  

#%% ADD THE 'YEAR' COLUMN IN THE 'PLAYERS' DATAFRAME
players = players %>%
  left_join(matches %>% select(MatchID, Year), by = "MatchID")
players

#%% MOST USED SHIRT NUMBERS FROM 1954 TO 2014
x = players[players$Year > 1950, ]

hist(x$Shirt.Number, breaks = 50, col = 'lightblue', border = 'black',
     xlab = 'Shirt Number', ylab = 'Number of times it has been used',
     main = 'Most Used Shirt Numbers From 1954 To 2014')
axis(1, at = unique(x$Shirt.Number), labels = unique(x$Shirt.Number))

#%% WE MODIFY THE COLUMN IN ORDER TO HAVE JUST NAT IN THE REFEREE COLUMN
matches$Referee = str_extract(matches$Referee, "\\((.*?)\\)")
matches$Referee = gsub("\\(|\\)", "", matches$Referee)
print(matches)

#%% HOW MANY MATCHES HAVE REFEREES OF EACH NATIONALITY DIRECTED?
ref_nationality = table(matches$Referee)
print(ref_nationality)

ref_nationality_filtered =ref_nationality[ref_nationality > 5] #We only show values greater than 5 in the graph to make it more readable
barplot(ref_nationality_filtered, 
        names.arg = names(ref_nationality_filtered), 
        xlab = 'Referee Nationality', 
        ylab = 'Number of matches',
        main = 'How Many Matches Have Referees Of Each Nationality Directed?',
        col = 'skyblue', 
        las = 2,
        cex.axis = 1,  
        cex.names = 0.4)
grid(lty = 1, col = "gray")


#%% TOTAL NUMBER OF GOALS SCORED IN GAMES REFEREED BY A REFEREE FROM A PARTICULAR NATION
dic = list()
for (referee in unique(matches$Referee)) {
  matches_referee = subset(matches, Referee == referee)
  if (nrow(matches_referee) > 5) {
    total_goals = sum(matches_referee$Home.Team.Goals + matches_referee$Away.Team.Goals)
    dic[[referee]] = total_goals
  }
}
print(dic)

df = data.frame(Referee = names(dic), Goals = unlist(dic), stringsAsFactors = FALSE)

barplot(df$Goals, names.arg = df$Referee,
        col = "skyblue",
        main = "Total Number Of Goals Scored In Games Directed By Each Referee",
        xlab = "Referee Nationality",
        ylab = "Total Goals",
        ylim = c(0, 170),
        las = 2,
        cex.names = 0.4)
grid(lty = 1, col = "gray")

#%% Mean of goal scored in games directed by a referee from a particular nation
##### NON FUNZIONA #####
media_goals_per_nazione = df %>%
  group_by(Referee) %>%
  summarize(MediaGoals = mean(Goals))

ggplot(media_goals_per_nazione, aes(x = Referee, y = MediaGoals)) +
  geom_bar(stat = "identity", fill = "blue", color = "black") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+
  labs(title = "Mean Of Goal Scored In Games Directed By A Referee From A Particular Nation",
       x = "Referee Nationality",
       y = "Goal per match")


#%% CREATE THE COLUMN 'Yellow or Red' IN THE PLAYERS DATAFRAME
lst = numeric(length(players$Event))
for (i in seq_along(players$Event)) {
  if (is.character(players$Event[i])) {
    if ('Y' %in% strsplit(players$Event[i], '')[[1]] || 'R' %in% strsplit(players$Event[i], '')[[1]]) {
      lst[i] <- 1
    } else {
      lst[i] <- 0
    }
  } else {
    lst[i] <- 0
  }
}
players$Yellow_or_Red = lst
table(players$Yellow_or_Red)
#MI VENGONO MENO 0 E MENO 1 ???

#%% CREATE THE COLUMN 'Cards' IN THE MATCHES DATAFRAME
card_per_match = numeric(length(players$MatchID))
for (i in seq_along(players$MatchID)) {
  if (!(players$MatchID[i] %in% names(card_per_match))) {
    card_per_match[[as.character(players$MatchID[i])]] = players$Yellow_or_Red[i]
  } else {
    card_per_match[[as.character(players$MatchID[i])]] = card_per_match[[as.character(players$MatchID[i])]] + players$Yellow_or_Red[i]
  }
}

matches$Cards = card_per_match[as.character(matches$MatchID)]
print(matches)

#%% TOTAL NUMBER OF CARDS GIVEN BY REFEREES OF A GIVEN NATIONALITY
#PRENDE IN CONSIDERAZIONE TUTTI GLI ARBITRI 
agg_data = matches %>%
  group_by(Referee) %>%
  summarize(TotalCards = sum(Cards))


ggplot(agg_data, aes(x = Referee, y = TotalCards)) +
  geom_bar(stat = "identity", fill = "blue", color = "black") +
  ggtitle('Total Number Of Cards Given By Referees Of A Given Nationality') +
  xlab('Referee Nationality') +
  ylab('Cards') +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))



