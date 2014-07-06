TITLE = "Wareztuga"
BASE_URL = "http://www.wareztuga.tv/"
ART  = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_SEARCH = 'icon-search.png'

#####################################################################
# This (optional) function is initially called by the PMS framework to
# initialize the plug-in. This includes setting up the Plug-in static
# instance along with the displayed artwork.
def Start():
    # Initialize the plug-in
    Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    
    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1 = TITLE
    ObjectContainer.view_group = 'List'
    ObjectContainer.art = R(ART)

    # Setup the default attributes for the other objects
    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)

    Login()

#####################################################################

@handler('/video/wareztuga', TITLE)
def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(title='Filmes', key=Callback(MoviesMenu)))
    oc.add(DirectoryObject(title=unicode('Séries'), key=Callback(SeriesMenu)))
    #oc.add(DirectoryObject(title='Anime', key=Callback(AnimeMenu)))
    return oc


@route('/video/wareztuga/movies', page=1)
def MoviesMenu(page=1):
    oc = ObjectContainer(title2='Filmes')

    element = HTML.ElementFromURL('http://www.wareztuga.tv/pagination.ajax.php?mediaType=movies&p='+str(page))
    movies_list = element.get_element_by_id('movies-list')
    
    for el in movies_list:
        oc.add(MovieObjectForElement(el))
    
    oc.add(NextPageObject(key=Callback(MoviesMenu, page=int(page)+1), title='Next'))
    
    return oc


@route('/video/wareztuga/series', page=1)
def SeriesMenu(page=1):
    oc = ObjectContainer(title2=unicode('Séries'))
    
    element = HTML.ElementFromURL('http://www.wareztuga.tv/pagination.ajax.php?mediaType=series&p='+str(page))
    series_list = element.get_element_by_id('series-list')
    
    for el in series_list:
        oc.add(SeriesObjectForElement(el))
    
    oc.add(NextPageObject(key=Callback(SeriesMenu, page=int(page)+1), title='Next'))
    
    return oc



def SeasonsMenu(title, url):
    html = HTML.ElementFromURL(url)
    seasons_list = html.xpath('//div[@class="season"]')
    oc = ObjectContainer(title2=title)
    i = 0
    for s in seasons_list:
        i += 1
        season_title = 'Temporada ' + str(s)
        season_url = BASE_URL + s.xpath('./a/@href')[0]
        season = SeasonObject(title=season_title + str(i),
                              index=i,
                              rating_key = season_url,
                              key = Callback(EpisodesMenu,
                                             series_title=title,
                                             season_number=i,
                                             url=season_url))
        oc.add(season)
    return oc


def EpisodesMenu(series_title, season_number, url):
    Log.Debug(series_title)
    Log.Debug(url)
    html = HTML.ElementFromURL(url)
    episodes_list = html.xpath('//div[@id="episodes-list"]/div[@class!="item nextepisodes"]')
    Log.Debug(episodes_list)
    oc = ObjectContainer(title2=series_title)
    for e in episodes_list:
        episode = EpisodeObject(show = series_title,
                                season = season_number,
                                thumb = BASE_URL + e.xpath('.//img/@src')[0],
                                title = e.xpath('.//img/@alt')[0],
                                url = BASE_URL + e.xpath('.//a/@href')[0])
        oc.add(episode)
    return oc


# Common parameters to Movies and TV Shows
# Element is the div for the media
def CommonParametersForElement(element):
    title = element.xpath('./div[1]/div[1]/@title')[0]
    url = BASE_URL + element.xpath('./div[1]/div[1]/a/@href')[0]
    thumb_url = BASE_URL + element.xpath('./div[1]/div[1]/a/img/@src')[0]
    summary = element.get_element_by_id('movie-synopsis-aux').text
    return {'title': title,
            'url': url,
            'thumb_url': thumb_url,
            'summary': summary}


# Parse HTML to get media information
def MovieObjectForElement(element):
    common = CommonParametersForElement(element)
    
    movie_info_div = element.xpath('./div[2]')[0]
    year = int(movie_info_div.xpath('//span[@class="year"]/span')[0].tail)
    
    return MovieObject(title=common['title'],
                       year=year,
                       summary=common['summary'],
                       thumb=common['thumb_url'],
                       url=common['url'])


def SeriesObjectForElement(element):
    common = CommonParametersForElement(element)
    
    nr_episodes = int(element.xpath('./div[1]/div[2]/span')[0].text)
    genres = element.xpath('./div[2]/div[@class="movie-detailed-info"]/span[@class="genre"]')[0].text.split(', ')
    
    return TVShowObject(title=common['title'],
                        summary=common['summary'],
                        thumb=common['thumb_url'],
                        key=Callback(SeasonsMenu, title=common['title'], url=common['url']),
                        rating_key=common['url'],
                        episode_count=nr_episodes,
                        genres=genres)


def Login():
    username = Prefs['username']
    password = Prefs['password']

    Log.Debug('===> Attempting to login user "%s"' % username)
    login_url = BASE_URL + 'login.ajax.php?username=%s&password=%s' % (username, password)
    login_request = HTTP.Request(url=login_url, immediate=True)
    login_response = login_request.content
    Log.Debug('===> Login returned "%s"' % login_response)

    if login_response == '0':
        return True
    return False