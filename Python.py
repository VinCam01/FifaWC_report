import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns',200)

matches = pd.read_csv('WorldCupMatches.csv')
players = pd.read_csv('WorldCupPlayers.csv')
wcups = pd.read_csv('WorldCups.csv')

print(matches.head())
print(players.head())
print(wcups.head())

print(matches.shape, players.shape, wcups.shape)

print(matches.info())
print(players.info())
print(wcups.info())

print(matches.isnull().sum(), '\n')
print(players.isnull().sum(), '\n')
print(wcups.isnull().sum())

matches = matches.dropna(how='all')
matches

print(matches.describe().T.round(2))
print(players.describe().T.round(2))
print(wcups.describe().T.round(2))

#GOAL SCORED FOR EACH WORLD CUP
plt.plot(wcups['Year'], wcups['GoalsScored'])
plt.xticks(wcups['Year'], rotation = 'vertical')
plt.yticks(range(70, 175, 10))
plt.grid()
plt.show()

#COUNTRY THAT WON THE MOST WORLD CUPS
wcups = wcups.replace('Germany FR', 'Germany')
plt.hist(wcups['Winner'],bins=15,edgecolor="black")
plt.xticks(wcups['Winner'], rotation = 'vertical')
plt.yticks(range(0, 10, 1))
#plt.title()
plt.grid(True)
plt.show()

#%% idea escludere mondiali antecedenti al 1938
print(matches[matches['Year'] > 1938].isnull().sum(), '\n')
print(players.isnull().sum(), '\n')
print(wcups.isnull().sum())

# AGGIUGNO LA COLONNA YEAR NEL DATAFRAME PLAYERS
players = pd.merge(players, matches[['MatchID', 'Year']], on='MatchID', how='left')

#%% NUMERI DI MAGLIA PIU' UTILIZZATI DAL 1954 AL 2014
x = players[players['Year']>1950]

plt.hist(x['Shirt Number'], bins = 50)
plt.xticks(players['Shirt Number'].unique())
#plt.ylim(1530, 1560)
plt.grid()
plt.show()

print(x)

#CONTO QUANTI REFEREE CI SONO PER OGNI NAZIONE
x['Shirt Number'].value_counts()

#ESTRAGGO SOLO LA SIGLA DEL REFEREE
matches['Referee'] = matches['Referee'].str.extract(r'\((.*?)\)')
#type(matches['Referee'])
matches

#CONTO QUANTI REFEREE CI SONO PER OGNI NAZIONE
ref_nationality = matches['Referee'].value_counts()
ref_nationality

#vediamo quali sono le nazionalità degli arbitri più frequenti, escludendo quelle minori di 5
ref_nationality = ref_nationality[ref_nationality>5]
plt.bar(ref_nationality.index, ref_nationality)
plt.xticks(rotation=90, ha='right', fontsize=5)
plt.show()

#Total number of goals scored in games refereed by a referee from a particular nation
dic = {}
for i in range(len(matches['Referee'])):
  if matches['Referee'][i] in ref_nationality:
    if matches['Referee'][i] not in dic:
      dic[matches['Referee'][i]] = matches['Home Team Goals'][i] + matches['Away Team Goals'][i]
    else:
      dic[matches['Referee'][i]] = dic[matches['Referee'][i]] + matches['Home Team Goals'][i] + matches['Away Team Goals'][i]

plt.bar(dic.keys(), dic.values())

plt.xlabel('Referee')
plt.ylabel('Goal Scored ')
plt.title('Total number of goals scored in games refereed by a referee from a particular nation ')
plt.grid()
plt.xticks(rotation=90, ha='right', fontsize=5)
plt.show()

#Mean of Goal by ref nationality
mean_gol_by_ref_nat = {}
for i in dic.keys():
  mean_gol_by_ref_nat[i] = (dic[i] / ref_nationality[i]).round(2)

plt.bar(mean_gol_by_ref_nat.keys(), mean_gol_by_ref_nat.values())

plt.xlabel('Referee')
plt.ylabel('Goal per match')
plt.title('Mean of Goal by ref nationality')
plt.grid()
plt.xticks(rotation=90, ha='right', fontsize=5)
plt.show()

#ADD THE COLUMN Yellow or Red IN THE DF PLAYERS
lst = []
for i in players['Event']:
  if type(i) == str:
    if 'Y' in i or 'R' in i:
      lst.append(1)
    else:
      lst.append(0)
  else:
    lst.append(0)
players['Yellow or Red'] = lst

players['Yellow or Red'].value_counts()

players

#CREO UNA COLONNA NEL DATAFRAME MATCHES COL NUMERO DI CARTELLINI DELLA PARTITA
card_per_match = {}
for i in range(len(players['MatchID'])):
  if players['MatchID'][i] not in card_per_match:
    card_per_match[players['MatchID'][i]] = players['Yellow or Red'][i]
  else:
    card_per_match[players['MatchID'][i]] = card_per_match[players['MatchID'][i]] + players['Yellow or Red'][i]

matches['Cards'] = matches['MatchID'].map(card_per_match)
matches

# QUANTI CARTELLINI DANNO GLI ARBITRI DI UNA DATA NAZIONALITA'?
dic = {}
for i in range(len(matches['Referee'])):
  if matches['Referee'][i] in ref_nationality:
    if matches['Referee'][i] not in dic:
      dic[matches['Referee'][i]] = matches['Cards'][i]
    else:
      dic[matches['Referee'][i]] = dic[matches['Referee'][i]] + matches['Cards'][i]

plt.bar(dic.keys(), dic.values())

plt.xlabel('Referee')
plt.ylabel('Cards ')
plt.title('Total number of cards given by ref of a given nationality ')
plt.grid()
plt.xticks(rotation=90, ha='right', fontsize=5)
plt.show()

# QUANTI CARTELLINI DANNO GLI ARBITRI DI UNA DATA NAZIONALITA' PER PARTITA?
mean_cards_by_ref_nat = {}
for i in dic.keys():
  mean_cards_by_ref_nat[i] = (dic[i] / ref_nationality[i]).round(2)

plt.bar(mean_cards_by_ref_nat.keys(), mean_cards_by_ref_nat.values())

plt.xlabel('Referee')
plt.ylabel('Cards per match')
plt.title('Cards of Goal by ref nationality')
plt.grid()
plt.xticks(rotation=90, ha='right', fontsize=5)
plt.show()

#HOW MANY GOAL HAS BEEN SCORED IN THESE SLOTS?
import re
def estrai_minuti_gol(a):
    minuti_gol = re.findall(r'G(\d+)', str(a))
    return [int(x) for x in minuti_gol]

players['Minuti_gol'] = players['Event'].apply(estrai_minuti_gol)

#SLOT 1-22 / 23-45 / 46-67 / 68-90
goal_scored_in_1_22=0
goal_scored_in_23_45=0
goal_scored_in_46_67=0
goal_scored_in_68_90=0

for i in players['Minuti_gol']:
  if i:
    for minute in i:
      if 1 <= minute < 23:
        goal_scored_in_1_22 += 1
      elif 23 <= minute < 46:
        goal_scored_in_23_45 += 1
      elif 46 <= minute < 68:
        goal_scored_in_46_67 += 1
      elif 68 <= minute <= 90:
        goal_scored_in_68_90 += 1

#print(goal_scored_in_1_22, goal_scored_in_23_45, goal_scored_in_46_67, goal_scored_in_68_90)
slot={'1/22':goal_scored_in_1_22, '23/45':goal_scored_in_23_45, '46/67':goal_scored_in_46_67,'68/90':goal_scored_in_68_90}
plt.bar(slot.keys(), slot.values())
plt.title('Gol in time slots')

#HOW MANY TIMES ITALY FINISH 1-2-3-4?
wcups
winner = 0
runner_up = 0
third = 0
fourth = 0

for i in wcups['Winner']:
  if i == 'Italy':
    winner += 1
for i in wcups['Runners-Up']:
  if i == 'Italy':
    runner_up += 1
for i in wcups['Third']:
  if i == 'Italy':
    third += 1
for i in wcups['Fourth']:
  if i == 'Italy':
    fourth += 1

italy = {'1 Place': winner, '2 Place': runner_up, '3 Place': third, '4 Place': fourth}

plt.pie(list(italy.values()), labels=list(italy.keys()), autopct='%1.1f%%')
plt.show()

# which are the most common combinations of first/second half result
winner=[]
first_half=[]
for i in range(len(matches)):
  if matches['Home Team Goals'][i] > matches['Away Team Goals'][i]:
    winner.append('First')
  elif matches['Home Team Goals'][i] < matches['Away Team Goals'][i]:
    winner.append('Second')
  else:
    winner.append('Draw')
  if matches['Half-time Home Goals'][i] > matches['Half-time Away Goals'][i]:
    first_half.append('First')
  elif matches['Half-time Home Goals'][i] < matches['Half-time Away Goals'][i]:
    first_half.append('Second')
  else:
    first_half.append('Draw')

matches['Winner Match'] = winner
matches['winner Half Time'] = first_half

#11 1D 12 DD D1 D2 21 2D 22

First_First = 0
First_Draw = 0
First_Second = 0
Draw_First = 0
Draw_Draw = 0
Draw_Second = 0
Second_First = 0
Second_Draw = 0
Second_Second = 0
for i in range(len(matches)):
  if matches['winner Half Time'][i] == 'First':
    if matches['Winner Match'][i] == 'First':
      First_First += 1
    elif matches['Winner Match'][i] == 'Draw':
      First_Draw += 1
    else:
      First_Second += 1
  elif matches['winner Half Time'][i] == 'Draw':
    if matches['Winner Match'][i] == 'First':
     Draw_First += 1
    elif matches['Winner Match'][i] == 'Draw':
      Draw_Draw += 1
    else:
      Draw_Second += 1
  else:
    if matches['Winner Match'][i] == 'First':
     Second_First += 1
    elif matches['Winner Match'][i] == 'Draw':
      Second_Draw += 1
    else:
      Second_Second += 1

combinations = {'1/1': First_First, '1/X': First_Draw, '1/2': First_Second,
                'X/1': Draw_First, 'X/X': Draw_Draw, 'X/2': Draw_Second,
                '2/1': Second_First, '2/X': Second_Draw, '2/2': Second_Second}

plt.pie(list(combinations.values()), labels=list(combinations.keys()), autopct='%1.1f%%')
plt.show()

matches.info()

#creo nuova colonna che indica se l'evento 1 tempo è uguale all'evento 2 tempo
first_second=[]
for i in range(len(matches)):
  if matches['winner Half Time'][i] == matches['Winner Match'][i]:
    first_second.append(1)
  else:
    first_second.append(0)
matches['first half outcome = second half outcome'] = first_second
matches

#correlazione
import seaborn as sns
corr_target_1 = round(matches[['Home Team Goals', 'Away Team Goals',
                               'Attendance', 'Half-time Home Goals',
                               'Half-time Away Goals','first half outcome = second half outcome',
                               'Cards']].corr(),2)

plt.figure(figsize = (18,6))
sns.heatmap(corr_target_1, annot = True, fmt='.2g',cmap= 'coolwarm')
plt.show()
