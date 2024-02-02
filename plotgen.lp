%%% 1. define the basic, recombinable elements of a story

% define all the narrative functions we can perform
function(
  introduce_character;
  complicate_relationship_between_characters;
  remove_character;
  make_reader_sad;
  make_reader_happy;
  make_reader_angry;
  end_the_story
).
% ... and so on

% define a story outline consisting of a fixed number of "scenes",
% each of which performs exactly one narrative function
scene(1..5).
{ scene_performs_function(S,F) : function(F) } = 1 :- scene(S).

%%% 2. define a bunch of rules that say how functions *can't* be combined

% example rule: the last scene always has to perform the end_the_story function
:- not scene_performs_function(5,end_the_story).

% example rule: we can't end the story before the last scene
:- scene_performs_function(S,end_the_story), S < 5.

% example rule: we have to introduce at least two characters
% before we can complicate a relationship between characters
:- scene_performs_function(S2,complicate_relationship_between_characters),
   0 { scene_performs_function(S1,introduce_character) : scene(S1), S1 < S2 } 1.

%%% 3. make sure output is displayed correctly

% only show the story outline in the completed answer set,
% not all the extra bookkeeping state
#show scene_performs_function/2.
