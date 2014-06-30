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

#####################################################################

@handler('/video/wareztuga', TITLE)
def MainMenu():
    #Login()
    oc = ObjectContainer()
    oc.add(DirectoryObject(title='Filmes', key=Callback(MoviesMenu)))
    #oc.add(DirectoryObject(title='Series', key=Callback(SeriesMenu)))
    #oc.add(DirectoryObject(title='Anime', key=Callback(AnimeMenu)))
    return oc


@route('/video/wareztuga/movies', page=1)
def MoviesMenu(page=1):
    oc = ObjectContainer(title2='Filmes')

    element = HTML.ElementFromURL('http://www.wareztuga.tv/pagination.ajax.php?mediaType=movies&p='+str(page))
    movies_list = element.get_element_by_id('movies-list')
    
    for el in movies_list:
        oc.add(ObjectForElement(el))
    
    oc.add(NextPageObject(key=Callback(MoviesMenu, page=int(page)+1), title='Next'))
    
    return oc


@route('/video/wareztuga/series', page=1)
def SeriesMenu(page=1):
    oc = ObjectContainer(title2='Series')
    
    element = HTML.ElementFromURL('http://www.wareztuga.tv/pagination.ajax.php?mediaType=series&p='+str(page))
    series_list = element.get_element_by_id('series-list')
    
    for el in series_list:
        oc.add(ObjectForElement(el))
    
    oc.add(NextPageObject(key=Callback(SeriesMenu, page=int(page)+1), title='Next'))
    
    return oc


# Parse HTML to get media information
def ObjectForElement(element):
    #Movie information
    movie_info_div = element.xpath('./div[2]')[0]
    title = movie_info_div.xpath('./a')[0].text
    url = BASE_URL + movie_info_div.xpath('./a/@href')[0]
    year = int(movie_info_div.xpath('//span[@class="year"]/span')[0].tail)
    summary = movie_info_div.get_element_by_id('movie-synopsis-aux').text
    
    # Thumbnail
    img_tag = element.xpath('./div[1]/div//img')[0]
    thumb_src = BASE_URL + img_tag.get('src')

    return MovieObject(title=title, year=year, summary=summary, thumb=thumb_src, url=url)


def Login():
    url = BASE_URL + 'login.ajax.php?username=%s&password=%s' % (Prefs['username'], Prefs['password'])
    request = HTTP.Request(url=url)
    Log.Debug('Login response is: %s' % request.content)


def Thumb(url):
    try:
        data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
        return DataObject(data, 'image/jpeg')
    except:
        return Redirect(R(ICON))
