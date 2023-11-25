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

#%% MEAN OF CARDS GIVEN BY REFEREES OF A GIVEN NATIONALITY
##MEDIA SBAGLIATAAAAAAAA
mean_cards_by_referee <- agg_data %>%
  mutate(MeanCards = TotalCards / n()) %>%
  select(Referee, MeanCards)

ggplot(mean_cards_by_referee, aes(x = Referee, y = MeanCards)) +
  geom_bar(stat = "identity", fill = "blue", color = "black") +
  ggtitle('Which Are The Strictest Referees?') +
  xlab('Referee Nationality') +
  ylab('Cards per match') +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))


#%% HOW MANY GOAL HAS BEEN SCORED IN THESE SLOTS?
#SLOT:  1-22 / 23-45 / 46-67 / 68-90
estrai_minuti_gol_2 = function(a) {
  minuti_gol = str_extract_all(as.character(a), "G(\\d+)")
  minuti_gol = unlist(minuti_gol)
  as.integer(gsub("G", "", minuti_gol))
}
players$Minuti_gol = sapply(players$Event, estrai_minuti_gol_2)

goal_scored_in_1_22 = 0
goal_scored_in_23_45 = 0
goal_scored_in_46_67 = 0
goal_scored_in_68_90 = 0

for (i in players$Minuti_gol) {
  if (length(i) > 0) {
    for (minute in i) {
      if (1 <= minute & minute < 23) {
        goal_scored_in_1_22 <- goal_scored_in_1_22 + 1
      } else if (23 <= minute & minute < 46) {
        goal_scored_in_23_45 <- goal_scored_in_23_45 + 1
      } else if (46 <= minute & minute < 68) {
        goal_scored_in_46_67 <- goal_scored_in_46_67 + 1
      } else if (68 <= minute & minute <= 90) {
        goal_scored_in_68_90 <- goal_scored_in_68_90 + 1
      }
    }
  }
}

slot = data.frame(
  Time_slot = c('1-22', '23-45', '46-67', '68-90'),
  Goals_scored = c(goal_scored_in_1_22, goal_scored_in_23_45, goal_scored_in_46_67, goal_scored_in_68_90)
)

barplot(slot$Goals_scored, names.arg = slot$Time_slot, xlab = 'Time slot', ylab = 'Goals scored', main = 'Number Of Goals Scored In Different Time Slots')

#%% HOW MANY TIMES ITALY FINISH 1-2-3-4?
winner = 0
runner_up = 0
third = 0
fourth = 0

for (i in wcups$Winner) {
  if (i == 'Italy') {
    winner = winner + 1
  }
}

for (i in wcups$Runners.Up) {
  if (i == 'Italy') {
    runner_up = runner_up + 1
  }
}

for (i in wcups$Third) {
  if (i == 'Italy') {
    third = third + 1
  }
}

for (i in wcups$Fourth) {
  if (i == 'Italy') {
    fourth = fourth + 1
  }
}

total = winner + runner_up + third + fourth
percentages = c(winner, runner_up, third, fourth) / total * 100

italy = data.frame(
  Place = c('1 Place', '2 Place', '3 Place', '4 Place'),
  Percent = percentages
)

ggplot(italy, aes(x = "", y = Percent, fill = Place)) +
  geom_bar(stat = "identity", width = 1, color = "white") +
  coord_polar(theta = "y") +
  theme_void() +
  labs(title = "How Will Italy's World Cup End If They Get Past The Quarter-Finals?") +
  geom_text(aes(label = paste0(Place, ": ", round(Percent, 1), "%")), 
            position = position_stack(vjust = 0.5))

#%% CREATE THE COLUMNS 'Winner Match' and 'Winner Half Time'
winner = character()
first_half = character()

for (i in 1:nrow(matches)) {
  if (matches$Home.Team.Goals[i] > matches$Away.Team.Goals[i]) {
    winner = c(winner, 'First')
  } else if (matches$Home.Team.Goals[i] < matches$Away.Team.Goals[i]) {
    winner = c(winner, 'Second')
  } else {
    winner = c(winner, 'Draw')
  }
  
  if (matches$Half.time.Home.Goals[i] > matches$Half.time.Away.Goals[i]) {
    first_half = c(first_half, 'First')
  } else if (matches$Half.time.Home.Goals[i] < matches$Half.time.Away.Goals[i]) {
    first_half = c(first_half, 'Second')
  } else {
    first_half = c(first_half, 'Draw')
  }
}

matches$`Winner Match` = winner
matches$`Winner Half Time` = first_half
 
#%% Which are the most common combinations of first/second half result?
#Possible combinations: 11 1X 12 XX X1 X2 21 2X 22
#VEDERE COME POSIZIONARE LE ETICHETTE+PERCENTUALI
First_First = 0
First_Draw = 0
First_Second = 0
Draw_First = 0
Draw_Draw = 0
Draw_Second = 0
Second_First = 0
Second_Draw = 0
Second_Second = 0

for (i in 1:nrow(matches)) {
  if (matches$`Winner Half Time`[i] == 'First') {
    if (matches$`Winner Match`[i] == 'First') {
      First_First = First_First + 1
    } else if (matches$`Winner Match`[i] == 'Draw') {
      First_Draw = First_Draw + 1
    } else {
      First_Second = First_Second + 1
    }
  } else if (matches$`Winner Half Time`[i] == 'Draw') {
    if (matches$`Winner Match`[i] == 'First') {
      Draw_First = Draw_First + 1
    } else if (matches$`Winner Match`[i] == 'Draw') {
      Draw_Draw = Draw_Draw + 1
    } else {
      Draw_Second = Draw_Second + 1
    }
  } else {
    if (matches$`Winner Match`[i] == 'First') {
      Second_First = Second_First + 1
    } else if (matches$`Winner Match`[i] == 'Draw') {
      Second_Draw = Second_Draw + 1
    } else {
      Second_Second = Second_Second + 1
    }
  }
}

total = sum(First_First, First_Draw, Draw_First, First_Second, Draw_Draw, Draw_Second, Second_First, Second_Draw, Second_Second)
percentages = c(First_First, First_Draw, Draw_First, First_Second, Draw_Draw, Draw_Second, Second_First, Second_Draw, Second_Second) / total * 100

combinations = data.frame(
  Combination = c('1/1', '1/X', 'X/1', '1/2', 'X/X', 'X/2', '2/1', '2/X', '2/2'),
  Count = c(First_First, First_Draw, Draw_First, First_Second, Draw_Draw, Draw_Second, Second_First, Second_Draw, Second_Second),
  Percentage = percentages
)

pie(combinations$Count, labels = paste0(combinations$Combination, "\n", round(combinations$Percentage, 1), "%"), col = rainbow(length(combinations$Combination)), main = 'First - Second Half Combinations')

#%% CREATE A NEW COLUMN '1Half = 2Half' IN THE MATCHES DATAFRAME
#the value will be 1 if the result of first half will be the same of the second, 0 otherwise
first_second = integer()

for (i in 1:nrow(matches)) {
  if (matches$`Winner Half Time`[i] == matches$`Winner Match`[i]) {
    first_second = c(first_second, 1)
  } else {
    first_second = c(first_second, 0)
  }
}

matches$`1Half = 2Half` = first_second
matches

#%% CORRELATION
selected_columns = c('Home.Team.Goals', 'Away.Team.Goals', 'Attendance', 
                      'Half.time.Home.Goals', 'Half.time.Away.Goals', 
                      '1Half = 2Half', 'Cards')

corr_target_1 = round(cor(matches[selected_columns]), 2)
par(mar = c(1, 1, 1, 1))
corrplot(corr_target_1, method = "square", type = "upper", order = "hclust", 
         addCoef.col = "black", tl.col = "black", tl.srt = 45, tl.cex = 0.7,
         col = colorRampPalette(c("blue", "white", "red"))(20))


