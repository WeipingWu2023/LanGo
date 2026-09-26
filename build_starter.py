"""Build the original, hand-written offline learning entries."""
import json
from pathlib import Path

data = {}


def add(word, pos, definition, example, synonyms=(), antonyms=()):
    entry = data.setdefault(word, [{'word': word, 'meanings': []}])[0]
    entry['meanings'].append({'partOfSpeech': pos, 'definitions': [{'definition': definition, 'example': example}],
                              'synonyms': list(synonyms), 'antonyms': list(antonyms)})


add('bright', 'adjective', 'Giving off a lot of light, or full of light.', 'The bright morning sun filled the kitchen.', ['brilliant', 'luminous'], ['dim', 'dark'])
add('bright', 'adjective', 'Quick to learn and understand things.', 'The bright student found a new way to solve the problem.', ['clever', 'intelligent'], ['unintelligent'])
add('bright', 'adjective', 'Cheerful or giving you a reason to feel hopeful.', 'Her bright smile made everyone feel welcome.', ['cheerful'], ['gloomy'])
add('brilliant', 'adjective', 'Extremely bright, impressive, or skillful.', 'Brilliant sunlight sparkled on the water.')
add('luminous', 'adjective', 'Producing or reflecting light, especially in the dark.', 'The luminous clock face was easy to read at night.')
add('dim', 'adjective', 'Giving little light; not easy to see clearly.', 'A dim lamp stood beside the bed.')
add('dark', 'adjective', 'Having little or no light.', 'The room was dark after we turned off the lamp.')
add('dark', 'noun', 'The absence of light.', 'We walked home before dark.')
add('clever', 'adjective', 'Able to understand, learn, or solve problems quickly.', 'That was a clever way to fix the broken handle.')
add('intelligent', 'adjective', 'Good at learning, understanding, and thinking carefully.', 'She asked an intelligent question about the experiment.')
add('unintelligent', 'adjective', 'Lacking good understanding or the ability to think things through.', 'One mistake does not mean a person is unintelligent.')
add('cheerful', 'adjective', 'Happy and positive in mood or manner.', 'His cheerful greeting helped me feel at home.')
add('gloomy', 'adjective', 'Sad and without much hope, or dark and unpleasant.', 'She felt gloomy after hearing the disappointing news.')
add('light', 'noun', 'The brightness that lets you see things.', 'Light came through the bedroom window.', ['illumination'], ['darkness'])
add('light', 'adjective', 'Not weighing very much.', 'This light backpack is comfortable to carry.', ['lightweight'], ['heavy'])
add('light', 'verb', 'To make something start burning or provide it with light.', 'We light a candle at dinner.', ['ignite'], ['extinguish'])
add('light', 'adverb', 'With little luggage or equipment, especially in the phrase travel light.', 'We travel light so we can move around easily.')
add('illumination', 'noun', 'Light that makes a place or object visible.', 'The desk lamp provides enough illumination for reading.')
add('darkness', 'noun', 'The state of having little or no light.', 'The power cut left the house in darkness.')
add('lightweight', 'adjective', 'Weighing less than similar things usually weigh.', 'I packed a lightweight jacket for the trip.')
add('heavy', 'adjective', 'Weighing a lot or requiring effort to lift.', 'The box was too heavy for me to carry alone.')
add('ignite', 'verb', 'To catch fire or make something catch fire.', 'A spark can ignite dry grass.')
add('extinguish', 'verb', 'To stop a fire or flame from burning.', 'Use water to extinguish the campfire completely.')
add('calm', 'adjective', 'Relaxed and free from strong worry, anger, or excitement.', 'She stayed calm during the difficult conversation.', ['relaxed', 'peaceful'], ['anxious', 'agitated'])
add('calm', 'noun', 'A quiet, peaceful state or period.', 'A sense of calm returned after the storm.', ['tranquility'], ['agitation'])
add('calm', 'verb', 'To make someone or something less upset or excited.', 'A familiar voice can calm a frightened child.', ['soothe'], ['agitate'])
add('relaxed', 'adjective', 'Feeling comfortable and not worried or tense.', 'I felt relaxed after a walk in the park.')
add('peaceful', 'adjective', 'Quiet and free from trouble or disturbance.', 'We spent a peaceful afternoon by the lake.')
add('anxious', 'adjective', 'Worried that something bad might happen.', 'He felt anxious before his first interview.')
add('agitated', 'adjective', 'Upset or nervous and unable to stay still or relaxed.', 'The long delay left the passengers agitated.')
add('tranquility', 'noun', 'A state of quiet and peace.', 'We enjoyed the tranquility of the empty garden.')
add('agitation', 'noun', 'A state of nervousness, worry, or restless excitement.', 'She paced around the room in agitation.')
add('soothe', 'verb', 'To make someone feel less upset or something feel less painful.', 'Soft music helped soothe the baby.')
add('agitate', 'verb', 'To make someone worried or upset; also, to shake or stir something.', 'The sudden noise seemed to agitate the horse.')

if __name__ == '__main__':
    Path(__file__).with_name('starter.json').write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
