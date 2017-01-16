from django.shortcuts import render
from django.http import JsonResponse
import requests
import random
import time
import csv
import sys
from bs4 import BeautifulSoup
import time
import codecs

# Create your views here.
def index(request):
    return render(request, 'index.html', context=None)

def ini_scrape(request):
    pagesScraped = 0;
    ctg = request.GET.get('ctgry', None)
    loc = request.GET.get('location', None)
    maxPageCnt = request.GET.get('pagesCnt', None)
    filelogname = request.GET.get('filelog', None)

    if maxPageCnt == '':
        maxPageCnt = 1
    else:
        maxPageCnt = int(maxPageCnt)

    with open('static/createdFiles/' + filelogname + '.csv', 'w', newline='') as fp:
        a = csv.writer(fp, delimiter=',')
        data = [
            ["Business Name", "Address", "Phone No.", "Website", "YP Page"]
        ]
        a.writerows(data)

    with open('static/createdFiles/' + filelogname + '.txt', 'w', newline='') as text_file:
        text_file.write('')

    def yppages_scrap(max_pages):

        page = 1
        while page <= max_pages:
            if page > 1:
                print("\nReinitializing connection...")
                appendnewlog("\nReinitializing connection...")
                time.sleep(10)  # delays for 10 seconds
            else:
                print("Initializing...\n")
                appendnewlog("Initializing...\n")

            indexrun = 0
            run_conn_server = False
            while (run_conn_server == False):
                if indexrun > 0:
                    print("\nConnection request failed, reinitializing connection...")
                    appendnewlog("\nConnection request failed, reinitializing connection...")

                run_conn_server = proxy_server(page, max_pages)
                indexrun = 1

            conn = run_conn_server

            #for checking request respons
            #with open('static/responsesHTML/' + str(page) + '.html', 'w', newline='') as html_file:
            #    html_file.write(run_conn_server)
            #end here

            for search_result in conn.findAll('div', {'class': 'search-results organic'}):
                for one_vcard in search_result.findAll('div', {'class': 'v-card'}):
                    for info_this_vcard in one_vcard.findAll('div', {'class': 'info'}):
                        try:
                            if info_this_vcard.find('h3', {'class': 'n'}):
                                for list_number in info_this_vcard.findAll('h3', {'class': 'n'}):
                                    lnumber = list_number.text
                                    print(lnumber)
                                for info in info_this_vcard.findAll('a', {'class': 'business-name'}):
                                    bname = info.text
                                    # print(bname)
                            else:
                                bname = "[NO BUSINESS NAME]"
                                # print("[Error getting business title]")

                            if info_this_vcard.find('div', {'class': 'info-primary'}):
                                if info_this_vcard.find('p', {'class': 'adr'}):
                                    address = info_this_vcard.find('p', {'class': 'adr'}).text
                                    # print(address)
                                else:
                                    address = "[NO ADDRESS SPECIFIED]"
                                    # print("Error getting address")

                                if info_this_vcard.find('div', {'class': 'phones'}):
                                    phoneNo = info_this_vcard.find('div', {'class': 'phones'}).text
                                    # print(phoneNo)
                                else:
                                    phoneNo = "[NO PHONE NUMBER FOUND]"
                                    # print("Error getting phone number")
                            else:
                                print("[Error getting primary info]")

                            if info_this_vcard.find('div', {'class': 'info-secondary'}):
                                if info_this_vcard.find('div', {'class': 'links'}):
                                    for info_links in info_this_vcard.findAll('div', {'class': 'links'}):
                                        if info_links.find('a', {'class': 'track-visit-website'}):
                                            for web_url in info_links.findAll('a', {'class': 'track-visit-website'}):
                                                company_site_url = web_url.get('href')
                                                # print(company_site_url)
                                        else:
                                            company_site_url = "[NO BUSINESS URL SITE]"
                                            # print("[NO BUSINESS URL SITE]")

                                        if info_links.find('a', {'class': 'track-more-info'}):
                                            for yp_url in info_links.findAll('a', {'class': 'track-more-info'}):
                                                yp_page_url = "http://www.yellowpages.com/" + yp_url.get('href')
                                                # print(yp_page_url)
                                        else:
                                            yp_page_url = "[NO YELLOW PAGE]"
                                            # print("[NO YELLOW PAGE]")
                                else:
                                    print("Error getting url links")
                            else:
                                print("[Error getting secondary info]")


                            with open('static/createdFiles/' + filelogname + '.csv', 'a', newline='') as f:
                                writer = csv.writer(f)
                                newdatarow = [
                                    [bname, address, phoneNo, company_site_url, yp_page_url]
                                ]
                                writer.writerows(newdatarow)

                            appendnewlog(lnumber+"\n")

                        except (AttributeError, KeyError):
                            print("Error: Check class name")

            for checkIfLast in conn.findAll('div', {'class': 'pagination'}):
                if checkIfLast.find('a', {'class': 'next ajax-page'}):
                    if page == max_pages:
                        print(" \nDONE!!!")
                        appendnewlog(" \nDONE!!!")
                    else:
                        print("\nSuccess PAGE " + str(page) + "! Proceeding to next page...PAGE " + str(page + 1)+"\n")
                        appendnewlog("\nSuccess PAGE " + str(page) + "! Proceeding to next page...PAGE " + str(page + 1)+"\n")
                else:
                    print(" \nDONE!!!")
                    appendnewlog(" \nDONE!!!")
                    pagesScraped = page
                    sys.exit()

            page += 1

    def proxy_server(pageNum, maxPageNum):
        searchTerms = ctg.replace(" ", "%20")
        geoLocationTerms = loc.replace(" ", "%20")
        geoLocationTermsFin = geoLocationTerms.replace(",", "%2C")

        if maxPageNum == 1:
            url = 'http://www.yellowpages.com/search?search_terms=' + searchTerms + '&geo_location_terms=' + geoLocationTermsFin
        else:
            url = 'http://www.yellowpages.com/search?search_terms=' + searchTerms + '&geo_location_terms=' + geoLocationTermsFin + '&page=' + str(
            pageNum)

        proxy_list = [
            "97.77.104.22:3128",
            "200.68.27.100:3128",
            "185.28.193.95:8080",
        ]

        user_agent_list = [
            "Mozilla/5.0 (compatible; U; ABrowse 0.6; Syllable) AppleWebKit/420+ (KHTML, like Gecko)",
            "Mozilla/5.0 (compatible; U; ABrowse 0.6;  Syllable) AppleWebKit/420+ (KHTML, like Gecko)",
            "Mozilla/5.0 (compatible; ABrowse 0.4; Syllable)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/53.0.2785.143 Chrome/53.0.2785.143 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (iPad; CPU OS 10_1_1 like Mac OS X) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0 Mobile/14B100 Safari/602.1",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 10_1_1 like Mac OS X) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0 Mobile/14B100 Safari/602.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
            "Mozilla/5.0 (Windows NT 5.1; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/601.7.8 (KHTML, like Gecko) Version/9.1.3 Safari/537.86.7",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.8 (KHTML, like Gecko) Version/9.1.3 Safari/601.7.8",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36 OPR/41.0.2353.56",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36 OPR/41.0.2353.56",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (iPad; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G36 Safari/601.1",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36"
        ]

        selected_proxy = random.choice(proxy_list)
        selected_user_agent = random.choice(user_agent_list)
        print("Selected proxy server is '" + selected_proxy + "'...")
        print("Selected user agent is '" + selected_user_agent + "'...")
        appendnewlog("\nSelected proxy server is '" + selected_proxy + "'...\nSelected user agent is '" + selected_user_agent + "'...")
        proxy = {"http": selected_proxy}
        header = {'User-agent': selected_user_agent}
        result = connect(url, proxy, selected_proxy, header)
        return result

    def connect(u, p, sp, h):
        try:
            response = ''
            while (response == ''):
                response = requests.get(u, headers=h, proxies=p, timeout=20)
                if response == '':
                    print("\nSomething went wrong! No response returned.")
                    appendnewlog("\nSomething went wrong! No response returned.")
                    return False

            soup = BeautifulSoup(response.text, "lxml")
            if soup.find('body', {'id': 'ERR_ACCESS_DENIED'}): #proxy server specific error
                print("\n")
                print("SQUID: Error - The requested URL could not be retrieved")
                appendnewlog("\nSQUID: Error - The requested URL could not be retrieved")
                time.sleep(2)
                return False
            elif soup.find('body', {'id': 'upgrade-browser'}): #yellowpage specific error
                print("\n")
                print("YP detects that User Agent "+h+" is outdated")
                appendnewlog("\nYP detects that User Agent "+h+" is outdated")
                time.sleep(2)
                return False
            else:
                appendnewlog("\n\n")
                return soup
        except requests.exceptions.ConnectTimeout as e:
            print("\n")
            print("Connection Timeout")
            print(e)
            appendnewlog("Connection Timeout\n")
            time.sleep(2)
            return False
        except requests.exceptions.ConnectionError as e:
            print("\n")
            print("Connection Error")
            print(e)
            appendnewlog("Connection Error\n")
            time.sleep(2)
            return False
        except requests.exceptions.HTTPError as e:
            print("\n")
            print("HTTP Error")
            print(e)
            appendnewlog("HTTP Error\n")
            time.sleep(2)
            return False
        except requests.exceptions.URLRequired as e:
            print("\n")
            print("URL Required")
            print(e)
            appendnewlog("URL Required\n")
            time.sleep(2)
            return False
        except requests.exceptions.TooManyRedirects as e:
            print("\n")
            print("Too Many Redirects")
            print(e)
            appendnewlog("Too Many Redirects\n")
            time.sleep(2)
            return False
        except requests.exceptions.ReadTimeout as e:
            print("\n")
            print("Read Timeout")
            print(e)
            appendnewlog("Read Timeout\n")
            time.sleep(2)
            return False
        except requests.exceptions.Timeout as e:
            print("\n")
            print("Timeout")
            print(e)
            appendnewlog("Timeout\n")
            time.sleep(2)
            return False
        except requests.exceptions.RequestException as e:
            print("\n")
            print("Request Error")
            print(e)
            appendnewlog("Request Error\n")
            time.sleep(2)
            return False

    def appendnewlog(wordinput):
        with open('static/createdFiles/' + filelogname + '.txt', 'a', newline='') as text_file:
            text_file.write(wordinput)

    yppages_scrap(maxPageCnt)

    data = {
        'f1': ctg,
        'f2': loc,
        'f3': pagesScraped,
        'f4': filelogname
    }
    return JsonResponse(data)
