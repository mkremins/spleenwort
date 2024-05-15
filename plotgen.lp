%%% 1. define the basic, recombinable elements of a story

% define all the narrative functions we can perform
function(
  introduce_character;
  introduce_rival_character;
  add_conflict_between_characters;
  add_bonding_between_characters;
  %make_reader_sad;
  %make_reader_happy;
  %make_reader_angry;
  %describe_setting;
  add_obstacle_towards_major_goal;
  add_obstacle;%a different one to test the obstacle type
  add_breakthrough;
  add_twist;
  level_up_obstacle
).

character_personality(
  sunny;
  cold;
  clumsy;
  smart;
  mysterious;
  quirky
).

obstacle_type(
  betrayal;
  forbidden_love;
  opposition;
  supernatural;
  guilt
).

% ... and so on

% define a story outline consisting of a fixed number of "scenes",
% each of which performs exactly one narrative function
#const num_scenes = 7.
scene(1..num_scenes).
{ scene_performs_function(S,F) : function(F) } = 1 :- scene(S).

% add personality for each introduced character
{ scene_introduce_personality(S,P) : character_personality(P) } = 1 :- scene_performs_function(S,introduce_character).

% assign a certain type to the obstacle
{ scene_define_obstacle_type(S,O) : obstacle_type(O) } = 1 :- scene_performs_function(S,add_obstacle).

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
%emotional_beat(make_reader_sad;make_reader_happy;make_reader_angry).
%:- scene_performs_function(S1,F1),
%   scene_performs_function(S2,F2),
%   emotional_beat(F1),
%   emotional_beat(F2),
%   S2 = S1 + 1.

% never introduce the same personality twice
:- scene_introduce_personality(S1,P), scene_introduce_personality(S2,P), S1 != S2.

% never introduce the same obstacle type twice
:- scene_define_obstacle_type(S1,P), scene_define_obstacle_type(S2,P), S1 != S2.

% always have some sort of character conflict
%:- { scene_performs_function(S,add_conflict_between_characters) } = 0.

% don't introduce more than 4 characters
:- { scene_performs_function(S1,introduce_character); scene_performs_function(S2,introduce_rival_character)} > 4.

% don't introduce more than 2 obstacles
:- { scene_performs_function(S1,add_obstacle); scene_performs_function(S2,add_obstacle_towards_major_goal)} > 2.

% always have some sort of obstacle
:- { scene_performs_function(S,add_obstacle) } = 0.

% never level up an obstacle until at least one obstacle is introduced
:- scene_performs_function(S1,level_up_obstacle), scene_performs_function(S2,add_obstacle), S1 < S2.

% always have an obstacle level up (for test)
:- { scene_performs_function(S,level_up_obstacle) } = 0.

% never level up the obstacle in the last scene
%:- scene_performs_function(S,level_up_obstacle), S = 7.

% never introduce a rival character in the first scene
:- scene_performs_function(S, introduce_rival_character), S = 1.

% never introduce a breakthrough in the first scene
:- scene_performs_function(S, add_breakthrough), S = 1.

% always have a breakthrough (for test)
%:- { scene_performs_function(S,add_breakthrough) } = 0.

% always have a bonding (for test)
%:- { scene_performs_function(S,add_bonding_between_characters) } = 0.

% always have a rival (for test)
:- { scene_performs_function(S, introduce_rival_character) } = 0.

% only add plot twist after the 3rd scene
:- scene_performs_function(S, add_twist), S <= 3.

% always have some sort of twist (for test)
:- { scene_performs_function(S,add_twist) } = 0.


%%% 3. make sure output is displayed correctly

% only show the story outline in the completed answer set,
% not all the extra bookkeeping state
#show scene_performs_function/2.
% show the personality
#show scene_introduce_personality/2.
% show the obstacle type
#show scene_define_obstacle_type/2.