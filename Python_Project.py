import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

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

#%% GOAL SCORED FOR EACH WORLD CUP
plt.plot(wcups['Year'], wcups['GoalsScored'], marker='o', markerfacecolor='gold', lw = 3, color='green')
plt.xlabel('World Cup')
plt.ylabel('Number of goal')
plt.xticks(wcups['Year'], rotation = 'vertical')
plt.yticks(range(70, 175, 10))
plt.grid()
plt.title('Goal Scored For Each World Cup')
plt.show()

#%% COUNTRIES THAT WON MOST WORLD CUPS
wcups = wcups.replace('Germany FR', 'Germany')
plt.hist(wcups['Winner'],bins=15,edgecolor="black")
plt.xlabel('Country')
plt.ylabel('Number of wins')
plt.xticks(wcups['Winner'], rotation = 'vertical')
plt.yticks(range(0, 10, 1))
plt.title('Who Won Most World Cups?')
plt.grid(True)
plt.show()

#%% TREND OF ATTENDANCE
mean_attendance = matches.groupby('Year')['Attendance'].mean().reset_index()

plt.plot(mean_attendance['Year'], mean_attendance['Attendance'], marker='o', markerfacecolor='black', lw = 3, color='royalblue')
plt.title('Trend of Attendance')
plt.xlabel('Year')
plt.ylabel('Attendance')
plt.xticks(mean_attendance['Year'], rotation = 'vertical')
plt.grid(True)
plt.show()

#%% ADD THE 'YEAR' COLUMN IN THE 'PLAYERS' DATAFRAME
players = pd.merge(players, matches[['MatchID', 'Year']], on='MatchID', how='left')

#%% MOST USED SHIRT NUMBERS FROM 1954 TO 2014
x = players[players['Year']>1950]

plt.hist(x['Shirt Number'], bins = 50)
plt.xlabel('Shirt Number')
plt.ylabel('Number of times it has been used')
plt.xticks(players['Shirt Number'].unique())
plt.grid()
plt.title('Most Used Shirt Numbers From 1954 To 2014')
comment = 'Although we see very particular numbers in national leagues, \nFIFA regulations state: "The shirt numbers of players must \ncorrespond to those indicated in the official team list (1 to 23)." \nSince Qatar 2022, the list is extended to 26 player'
plt.text(1.02, 0.5, comment, ha='left', va='center', transform=plt.gcf().transFigure, fontsize=10)
plt.show()

#%% HOW MANY MATCHES HAVE REFEREES OF EACH NATIONALITY DIRECTED?
'''
Referee column is structured in this form : Name Surname (NAT)
Since we just need their nationality, we modify the column in order to have just NAT
'''
matches['Referee'] = matches['Referee'].str.extract(r'\((.*?)\)')
ref_nationality = matches['Referee'].value_counts()
ref_nationality

ref_nationality = ref_nationality[ref_nationality>5]   #We only show values greater than 5 in the graph to make it more readable 
colori_sfumati = [plt.cm.viridis(i / len(ref_nationality)) for i in range(len(ref_nationality))]
plt.bar(ref_nationality.index, ref_nationality, color=colori_sfumati)
plt.xlabel('Referee Nationality')
plt.ylabel('Number of matches')
plt.xticks(rotation=90, ha='right', fontsize=5)
plt.title('How Many Matches Have Referees Of Each Nationality Directed?')
plt.show()

#%% TOTAL NUMBER OF GOALS SCORED IN GAMES DIRECTED BY A REFEREE FROM A PARTICULAR NATION
dic = {}
for i in range(len(matches['Referee'])):
  if matches['Referee'][i] in ref_nationality:
    if matches['Referee'][i] not in dic:
      dic[matches['Referee'][i]] = matches['Home Team Goals'][i] + matches['Away Team Goals'][i]
    else:
      dic[matches['Referee'][i]] = dic[matches['Referee'][i]] + matches['Home Team Goals'][i] + matches['Away Team Goals'][i]

colori_sfumati = [plt.cm.brg(i / len(ref_nationality)) for i in range(len(ref_nationality))]
plt.bar(dic.keys(), dic.values(), color=colori_sfumati)
plt.xlabel('Referee Nationality')
plt.ylabel('Goal Scored ')
plt.title('Total Number Of Goals Scored In Games Directed By A Referee From A Particular Nation')
plt.grid()
plt.xticks(rotation=90, ha='right', fontsize=5)
plt.show()

#%% MEAN OF GOAL SCORED IN GAMES DIRECTED BY A REFEREE FROM A PARTICULAR NATION
mean_gol_by_ref_nat = {}
for i in dic.keys():
  mean_gol_by_ref_nat[i] = (dic[i] / ref_nationality[i]).round(2)

colori_sfumati = [plt.cm.ocean(i / len(ref_nationality)) for i in range(len(ref_nationality))]
plt.bar(mean_gol_by_ref_nat.keys(), mean_gol_by_ref_nat.values(), color=colori_sfumati)
plt.xlabel('Referee Nationality')
plt.ylabel('Goal per match')
plt.title('Mean Of Goal Scored In Games Directed By A Referee From A Particular Nation')
plt.grid()
plt.xticks(rotation=90, ha='right', fontsize=5)
plt.show()

#%% CREATE THE COLUMN 'Yellow or Red' IN THE PLAYERS DATAFRAME
'''
For each player the value will be 1 if he received a cards, 0 otherwise
'''
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

#%% CREATE THE COLUMN 'Cards' IN THE MATCHES DATAFRAME
'''
For each match, this value represent the number of yellow or red card given by the referee
'''
card_per_match = {}
for i in range(len(players['MatchID'])):
  if players['MatchID'][i] not in card_per_match:
    card_per_match[players['MatchID'][i]] = players['Yellow or Red'][i]
  else:
    card_per_match[players['MatchID'][i]] = card_per_match[players['MatchID'][i]] + players['Yellow or Red'][i]

matches['Cards'] = matches['MatchID'].map(card_per_match)
print(matches)

#%% TOTAL NUMBER OF CARDS GIVEN BY REFEREES OF A GIVEN NATIONALITY
dic = {}
for i in range(len(matches['Referee'])):
  if matches['Referee'][i] in ref_nationality:
    if matches['Referee'][i] not in dic:
      dic[matches['Referee'][i]] = matches['Cards'][i]
    else:
      dic[matches['Referee'][i]] = dic[matches['Referee'][i]] + matches['Cards'][i]

colori_sfumati = [plt.cm.jet(i / len(ref_nationality)) for i in range(len(ref_nationality))]
plt.bar(dic.keys(), dic.values(), color=colori_sfumati)
plt.xlabel('Referee Nationality')
plt.ylabel('Cards')
plt.title('Total Number Of Cards Given By Referees Of A Given Nationality ')
plt.grid()
plt.xticks(rotation=90, ha='right', fontsize=5)
plt.show()

#%% MEAN OF CARDS GIVEN BY REFEREES OF A GIVEN NATIONALITY
mean_cards_by_ref_nat = {}
for i in dic.keys():
  mean_cards_by_ref_nat[i] = (dic[i] / ref_nationality[i]).round(2)

colori_sfumati = [plt.cm.gnuplot(i / len(ref_nationality)) for i in range(len(ref_nationality))]
plt.bar(mean_cards_by_ref_nat.keys(), mean_cards_by_ref_nat.values(), color=colori_sfumati)
plt.xlabel('Referee Nationality')
plt.ylabel('Cards per match')
plt.title('Which Are The Strictest Referees?')
plt.grid()
plt.xticks(rotation=90, ha='right', fontsize=5)
plt.show()

#%% HOW MANY GOAL HAS BEEN SCORED IN THESE SLOTS?
'''
SLOT:  1-22 / 23-45 / 46-67 / 68-90
'''
def estrai_minuti_gol(a):
    minuti_gol = re.findall(r'[GP](\d+)', str(a))
    return [int(x) for x in minuti_gol]

players['Minuti_gol'] = players['Event'].apply(estrai_minuti_gol)

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

slot={'1-22':goal_scored_in_1_22, '23-45':goal_scored_in_23_45, '46-67':goal_scored_in_46_67,'68-90':goal_scored_in_68_90}
plt.bar(slot.keys(), slot.values())
plt.xlabel('Time slot')
plt.ylabel('Goals scored')
plt.title('Number Of Goals Scored In Different Time Slots')
plt.show()

#%% MEAN OF GOALS IN GROUP STAGE MATCHES VS MEAN OF GOALS IN KNOCKOUT MATCHES
matches['Stage'].unique()

for i in range(len(matches['Stage'])):
    if 'Group' in matches['Stage'][i] or matches['Stage'][i]  == 'Preliminary round' or matches['Stage'][i]  == 'First round':
        matches['Stage'][i] = 'Group'
    else:
        matches['Stage'][i] = 'Knockout'
      
matches['total_goals'] = matches['Home Team Goals'] + matches['Away Team Goals']

tab1 = matches.groupby(['Year', 'Stage'])['total_goals'].mean().reset_index()
tab2 = tab1.pivot(index='Year', columns='Stage', values='total_goals').reset_index()
tab2_mod = tab2[tab2['Year'] >= 1954]

plt.plot(tab2_mod['Year'], tab2_mod['Group'], label = 'Group Stage', marker='o', markerfacecolor='red', lw = 2, color='red')
plt.plot(tab2_mod['Year'], tab2_mod['Knockout'],label = 'Knockout Stage',  marker='o', markerfacecolor='#5A9BD5', lw = 2, color='#5A9BD5')
plt.xlabel('World Cup')
plt.ylabel('Mean of goal')
plt.xticks(tab2_mod['Year'], rotation = 'vertical')
plt.legend()
plt.grid()
plt.title('MEAN OF GOALS IN GROUP STAGE MATCHES VS MEAN OF GOALS IN KNOCKOUT MATCHES')
plt.show()

#%% HOW MANY TIMES ITALY FINISH 1-2-3-4?
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
plt.title("How Will Italy's World Cup End If They Get Past The Quarter-Finals?")
comment = '1 Place: ' + str(winner) + ' times' + '\n2 Place: ' + str(runner_up) + ' times' + '\n3 Place: ' + str(third) + ' time' + '\n4 Place: ' + str(fourth) + ' time'
plt.text(1.02, 0.5, comment, ha='left', va='center', transform=plt.gcf().transFigure, fontsize=10)
plt.show()

#%% CREATE THE COLUMNS 'Winner Match' and 'Winner Half Time'
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
matches['Winner Half Time'] = first_half

#%% Which are the most common combinations of first/second half result?
'''
Possible combinations: 11 1X 12 XX X1 X2 21 2X 22
'''
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
  if matches['Winner Half Time'][i] == 'First':
    if matches['Winner Match'][i] == 'First':
      First_First += 1
    elif matches['Winner Match'][i] == 'Draw':
      First_Draw += 1
    else:
      First_Second += 1
  elif matches['Winner Half Time'][i] == 'Draw':
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

combinations = {'1/1': First_First, '1/X': First_Draw,'X/1': Draw_First,
                '1/2': First_Second, 'X/X': Draw_Draw, 'X/2': Draw_Second,
                '2/1': Second_First, '2/X': Second_Draw, '2/2': Second_Second}

plt.gcf().set_size_inches(6, 7)
plt.pie(list(combinations.values()), labels=list(combinations.keys()), autopct='%1.1f%%', startangle=0)
plt.title('First - Second Half Combinations')
plt.show()



#%% CREATE A NEW COLUMN '1Half = 2Half' IN THE MATCHES DATAFRAME
'''
the value will be 1 if the result of first half will be the same of the second, 0 otherwise
'''
first_second=[]
for i in range(len(matches)):
  if matches['Winner Half Time'][i] == matches['Winner Match'][i]:
    first_second.append(1)
  else:
    first_second.append(0)
matches['1Half = 2Half'] = first_second
matches

#%% CORRELATION
corr_target_1 = round(matches[['Home Team Goals', 'Away Team Goals',
                               'Attendance', 'Half-time Home Goals',
                               'Half-time Away Goals','1Half = 2Half',
                               'Cards']].corr(),2)

plt.figure(figsize = (18,6))
plt.title('Correlation Heatmap')
sns.heatmap(corr_target_1, annot = True, fmt='.2g',cmap= 'coolwarm')
plt.show()

#World Cup Podium
winner = wcups['Winner'].value_counts()
runnerup = wcups['Runners-Up'].value_counts()
third = wcups['Third'].value_counts()

wrt = pd.concat([winner, runnerup, third], axis = 1)
wrt.fillna(0, inplace = True)
wrt = wrt.astype(int)
wrt

wrt['Total'] = wrt['Winner'] + wrt['Runners-Up'] + wrt['Third']
wrt['Final'] = wrt['Winner'] + wrt['Runners-Up']
wrt

wrt.index.dtype
wrt.index = wrt.index.astype(str)
wrt = wrt.reset_index(drop=False)
wrt

wrt.rename(columns={'index': 'Team'},inplace = True)
wrt.columns

countries = np.unique(matches[['Home Team Name', 'Away Team Name']].values)

countries_df = pd.DataFrame(countries)
countries_df.rename(columns={0: 'Team'},inplace = True)

m_df = pd.merge(wrt,countries_df, on='Team', how='right')
m_df.fillna(0, inplace=True)
m_df

m_df["Highest"] = m_df.apply(lambda row: 'Winner' if row['Winner'] > 0 
                        else ('Runners-Up' if row['Runners-Up'] > 0 
                                else ('Third' if row['Third'] > 0 else 'Qualified')), axis=1)
m_df

# MAP
map = px.choropleth(m_df, 
                    locations='Team',
                    locationmode='country names',
                    color='Highest',
                    hover_name='Team',
                    projection='natural earth')

map.show()

