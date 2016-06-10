import requests
import json
import sqlite3 as lite
import sys
import re
import urllib

spotify_api = 'TCLQLMNCNHHGKWDSI'
# access_token = "BQAmGRxb2r_GYnnb7x-_NGbNsyu2M8q1LgsMgXa62vgm2MSYNlBfRTMOecvrg30FfktzNfpKpOaGkhlPx6UVxLF-qdfNizIumvM1IeczQ6kYcWXZSLvqK5LnyZR4bsOCkgP3ElhuOqfcRUolJwAgPNl6o2cV32yIxhhdKqZdzJhfGC2mY2PpsxJkexsjt2j8FCjGQm47bnUMjyOSracnkFOa5ALUO56bHke8a507EsqrzE4wM-Giz0etX22DQ30fmff5ylJv"
# headers = {'Authorization' : 'Bearer ' + access_token}





def post_playlist(environ):
  con = lite.connect ('spotify.db')
  cursor = con.cursor()
  #if not environ['QUERY_STRING']:
      #return
  #sys.stderr.write(str(environ))
  args=urllib.parse.parse_qs(environ['QUERY_STRING'])
  access_token = args['access_token'][0]
  user = args['user'][0]
  print(access_token)
  headers = {'Authorization' : 'Bearer ' + access_token}
  #get and save user playlists in sql table 'playlists'
  getlist = "https://api.spotify.com/v1/users/"+ user +"/playlists"
  resp = requests.get (getlist, headers=headers)
  data = json.loads(resp.text)
  print(data)
  gettracks = []
  for item in data['items']:
      gettracks.append([user, item['name'],item['owner']['id'],item['tracks']['href']])
      #cursor.execute ('create table playlists (user,listOwner,name,href)')
  for track in gettracks:
      cursor.execute('insert into playlists (user, name, listOwner, href) VALUES (?,?,?,?)',track)
      con.commit()
  cursor.execute('select * from playlists where user = user')
  playlists=cursor.fetchall()
  #for list in playlists:
      #print(list)

 #get discover weekly track from api and use track ID to generate request for audio features.
 #audio features are stored in database table tracks
  cursor = con.cursor()
  cursor.execute('select href from playlists where name = "Discover Weekly" and user = ?',user)
  print (user)
  con.text_factory = str
  hrefquery = cursor.fetchone()
  url = (hrefquery[0])
  #print(url)
  resp = requests.get(url, headers=headers)
  data = json.loads(resp.text)
  playlist=[]
  #cursor.execute('create table tracks (id text,uri text,danceability number, energy number, key number, loudness number, mode number, speechiness number, acousticness number, instrumentalness number, liveness number, valence number, tempo number, camelot_key text, rank number)')
  for track in data['items']:
    id = (track['track']['id'])
    resp = requests.get('https://api.spotify.com/v1/audio-features/'+ id, headers=headers)
    audiofeatures = json.loads(resp.text)
    audiofeatures['user']=user 
    cursor.execute('insert into tracks (id, uri, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, user) '
             'Values(:id, :uri, :danceability, :energy, :key, :loudness, :mode,:speechiness, :acousticness, :instrumentalness, :liveness, :valence, :tempo, :user)',
             audiofeatures)
  con.commit()
  cursor.execute('update tracks set camelot_key = (select camelot_key from note_map where note_map.echo_nest_key = tracks.key AND note_map.mode = tracks.mode)')
  cursor.execute('update tracks set rank = (select rank from note_map where tracks.camelot_key = note_map.camelot_key)')
  con.commit()



#create new playlist in spotify
  url = "https://api.spotify.com/v1/users/"+user+"/playlists"
  body = {
   "name":"Hello World",
   "public": 'false'
  }
  resp=requests.post(url, headers=headers, data=json.dumps(body))
  response=json.loads(resp.text)
  newlisturl = (response['href'])
  newlistredirect = (response['external_urls']['spotify'])
  newlistredirectbyte = newlistredirect.encode(encoding="utf-8")


   #use new playlist url to post tracks to new playlist.
  user = args['user'][0]
  con.text_factory = str #returns cursor results in string
  cursor.execute ('select uri, camelot_key, rank, tempo from tracks where user = ? group by camelot_key, tempo order by mode desc',user)
  rows = cursor.fetchall()
  uris= [row[0] for row in rows] #converts cursor query results to list
  for uri in uris:
       url2 = (newlisturl+"/tracks?uris="+uri)
       resp2 = requests.post (url2, headers=headers)
       #print (url2)
       #response2 = json.loads (resp2.text)
       #print (response2)
  #print(tracklist)
  #print(rows)
  location_json = {
    'location': newlistredirect
  }
  print(newlistredirectbyte)
  return (newlistredirectbyte)
  user = args['user'][0]
  cursor.execute ('delete from tracks where user = ?',user)
  cursor.execute ('delete from playlists where user = ?',user)
  con.commit()
  con.close()
  sys.exit([0])













#move tracks from python list to sql table














#con = lite.connect ('spotify.db')
#cursor = con.cursor()
#cursor.execute ('select charindex(':', 'spotify:track:6ce5ozgjHE0JoYlIpk4WYN')')
#output = cursor.fetchall()
#print(output)















#url = "http://developer.echonest.com/api/v4/track/profile?"
#track = "spotify-WW:track:3Ue6KAFvPDcHzacdJJNBwH"
#params = {'format':'json','id':track,'bucket':'audio_summary','api_key': spotify_api}
#r = requests.get(url, params=params)
#r.json()






