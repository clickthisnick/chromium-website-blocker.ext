function extractDomain(url) {
    return url.replace(/^(?:https?:\/\/)?(?:[^\/]+\.)?([^.\/]+\.[^.\/]+).*$/, "$1");
}

// Urls to never block even tho the domain itself might be blocked
// Can be a full url like https://an.example.com
const allowedList = [

]
const allowedSet = new Set(allowedList)

// List of domains to block
// Must be just the domain (example.com not an.example.com)
// You will need to allow specific subdomains or queries within a blocked domain
const blockedList = [
    "example.com",
]
const blockedSet = new Set(blockedList)

// Urls that are allowed as long as you have another tab open with a specific url.
// Usecase is lets say you only want to allow music sites if you are also on github
// Value is used with startsWith() so can be a full url like https://an.example.com
// Key is an exact match
const allowedIfAlsoHaveAnotherTabOpen = {
    "http://www.example.com/": "https://github.com/"
}

const today = new Date();
const dd = String(today.getDate()).padStart(2, '0');
const mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
const yyyy = today.getFullYear();


const unlockCounterVar = `chromium-website-blocker-counter-${mm}-${dd}-${yyyy}`

// 60000 milliseconds in 1 minute
// 300000 milliseconds in 5 minutes
// 900000 milliseconds in 15 minutes
const millisecondsLimit = 300000

function getMillisecondTime(pastMilliseconds = 0) {
    let date = new Date();
    return String(date.getTime() - pastMilliseconds);
}

function isAboveThreshold(millisecondString) {
    return getMillisecondTime() - parseInt(millisecondString) > millisecondsLimit
}

function toggleUrl(url, inputText) {
    console.log(`toggle ${url}`)

    if (document.getElementById("input").value != inputText) {
        console.log('Wrong Input Text')
    } else {
        let dateString = localStorage.getItem(url)
        let counter = localStorage.getItem(unlockCounterVar)
        let counterInt = Number(counter)
        counterInt++
        localStorage.setItem(unlockCounterVar, counterInt)

        document.getElementById("counter").text = counterInt

        if (isAboveThreshold(dateString)) {
            localStorage.setItem(url, getMillisecondTime())
            document.getElementById(url).value = "Enable"
        } else {
            localStorage.setItem(url, getMillisecondTime(millisecondsLimit))
            document.getElementById(url).value = "Disable" 
        }
    }
}

function init() {
    // Disable sites to begin with
    for(i = 0; i < blockedList.length; i++) {
        let url = blockedList[i]

        // set item in local storage
        // local storage has string values
        const millisecondsString = localStorage.getItem(url)
        if (millisecondsString === null) {
            localStorage.setItem(url, getMillisecondTime(millisecondsLimit))
        }
     }
}

function generateHtml(tab) {
    // Generate html, but hide website names so you dont get influenced to click a different site
    const div = document.getElementById('sites');

    let url = tab.url.split('blocked.html?url=')
    if (url.length === 1){ 
        url = url[0]
    } else {
        url = url[1]
    }

    url = extractDomain(url)

    const millisecondsString = localStorage.getItem(url)
    const text = isAboveThreshold(millisecondsString) ? "Disable" : "Enable"
    const enterText = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    div.innerHTML += "Enter This String:<br>"
    div.innerHTML += `${enterText}<br><br>`
    div.innerHTML += `<input id="input" type="input" value=""></input><br>`
    div.innerHTML += `<input id="${url}" type="button" value="${text}"></input><br><br>`
    div.innerHTML += `You've unlocked <span id="counter"></span> times today.<br><span id="counterWastedTime">`

    // Set our timer counter
    const unlockCounterString = localStorage.getItem(unlockCounterVar)
    if (unlockCounterString === null) {
        localStorage.setItem(unlockCounterVar, 0)
        document.getElementById('counter').innerText = "0";
    } else {
        document.getElementById('counter').innerText = unlockCounterString;
        document.getElementById('counterWastedTime').innerText = `Wasting ${Number(unlockCounterString) * 5} minutes`
    }

    document.getElementById(url).addEventListener("click", function(){toggleUrl(url, enterText)});
}

function run(tabs) {
    
    const tabUrls = tabs.map((tab) => {
        return tab.url
    })

    tabs.forEach((tab) => {
        // Skip any tab that is not on a url
        if (tab.url.search(/https?:/) !== 0) {
            return;
        };

        // Get the current domain of the tab
        const currentDomain = extractDomain(tab.url)

        if (blockedSet.has(currentDomain)) {
            // Skip blocking if the url is in the allowedList
            for (i = 0; i < allowedList.length; i++) {
                if (tab.url.startsWith(allowedList[i])) {
                    return;
                }
            }

            // Skip blocking if any tab is open that allows this url
            if (tab.url in allowedIfAlsoHaveAnotherTabOpen) {
                const tabUrlThatMustAlsoBeOpen = allowedIfAlsoHaveAnotherTabOpen[tab.url]
                for (i = 0; i < tabUrls.length; i++) {
                    if (tabUrls[i].startsWith(tabUrlThatMustAlsoBeOpen)) {
                        return;
                    }
                }
            }

            // Make sure its true in local storage
            const urlValue = localStorage.getItem(currentDomain)

            if (isAboveThreshold(urlValue)) {
                const redirect = chrome.extension.getURL('blocked.html') + '?url=' + encodeURIComponent(currentDomain);

                chrome.tabs.update(tab.id, { url: redirect });

                return;
            }
        }
    })

    return true;
}

chrome.tabs.onCreated.addListener(function(tab) {
    chrome.tabs.getAllInWindow(tab.windowId, function(tabs) {
        run(tabs)    
    })
});

chrome.tabs.onActivated.addListener(function(info) {
    chrome.tabs.get(info.tabId, function(tab) {
        chrome.tabs.getAllInWindow(tab.windowId, function(tabs) {
            run(tabs)    
        })
    });
});

chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
    if (changeInfo.status === 'loading') {
        chrome.tabs.getAllInWindow(tab.windowId, function(tabs) {
            run(tabs)    
            return
        })
    }
});

init()

chrome.tabs.query({active: true, lastFocusedWindow: true}, tabs => {
    generateHtml(tabs[0]);
    // use `url` here inside the callback because it's asynchronous!
});
