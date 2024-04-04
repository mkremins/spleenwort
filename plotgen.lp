%%% 1. define the basic, recombinable elements of a story

% define all the narrative functions we can perform
function(
  introduce_character;
  % describe_setting;
  add_conflict_between_characters;
  add_bonding_between_characters;
  %make_reader_sad;
  %make_reader_happy;
  %make_reader_angry;
  add_obstacle_towards_major_goal;
  add_breakthrough_towards_major_goal
).

character_personality(
  sunny;
  cold;
  clumsy;
  smart;
  mysterious;
  quirky
).

% ... and so on

% define a story outline consisting of a fixed number of "scenes",
% each of which performs exactly one narrative function
#const num_scenes = 7.
scene(1..num_scenes).
{ scene_performs_function(S,F) : function(F) } = 1 :- scene(S).

%% add personality for each introduced character
{ scene_introduce_personality(S,P) : character_personality(P) } = 1 :- scene_performs_function(S,introduce_character).



%%% 2. define a bunch of rules that say how functions *can't* be combined

% never add conflict between characters until we've introduced at least two
:- scene_performs_function(S2,add_conflict_between_characters),
   0 { scene_performs_function(S1,introduce_character) : scene(S1), S1 < S2 } 1.

% never add bonding between characters until we've introduced at least two
:- scene_performs_function(S2,add_bonding_between_characters),
   0 { scene_performs_function(S1,introduce_character) : scene(S1), S1 < S2 } 1.

% never perform the same function twice in a row
:- scene_performs_function(S1,F),
   scene_performs_function(S2,F),
   S2 = S1 + 1.

% never do two emotional beats in a row
emotional_beat(make_reader_sad;make_reader_happy;make_reader_angry).
:- scene_performs_function(S1,F1),
   scene_performs_function(S2,F2),
   emotional_beat(F1),
   emotional_beat(F2),
   S2 = S1 + 1.

% how to restrict not add the same personality twice?
% never introduce the same personality twice
:- scene_introduce_personality(S1,P), scene_introduce_personality(S2,P), S1 != S2.

% always have some sort of character conflict
:- { scene_performs_function(S,add_conflict_between_characters) } = 0.

%%% 3. make sure output is displayed correctly

% only show the story outline in the completed answer set,
% not all the extra bookkeeping state
#show scene_performs_function/2.
% show the personality
#show scene_introduce_personality/2.
