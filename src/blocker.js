function extractDomain(url) {
    return url.replace(/^(?:https?:\/\/)?(?:[^\/]+\.)?([^.\/]+\.[^.\/]+).*$/, "$1");
}

// List of domains to block
const blockedList = [
    "example.com",
]

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

function toggleUrl(url) {
    console.log(`toggle ${url}`)

    let dateString = localStorage.getItem(url)

    if (isAboveThreshold(dateString)) {
        localStorage.setItem(url, getMillisecondTime())
        document.getElementById(url).value = "Enable"
    } else {
        localStorage.setItem(url, getMillisecondTime(300000))
        document.getElementById(url).value = "Disable" 
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
            localStorage.setItem(url, getMillisecondTime(300000))
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
    div.innerHTML += "<br>"
    div.innerHTML += "Current Site:"
    div.innerHTML += `<input id="${url}" type="button" value="${text}"></input>`
    div.innerHTML += "<br>"

    document.getElementById(url).addEventListener("click", function(){toggleUrl(url)});
}

function run(tab) {

    // Skip any tab that is not on a url
    if (tab.url.search(/https?:/) !== 0) {
        return;
    };

    // Get the current domain of the tab
    const currentDomain = extractDomain(tab.url)

    blockedList.forEach((url) => {
        if (currentDomain === url) {
            // Make sure its true in local storage
            const urlValue = localStorage.getItem(url)

            if (isAboveThreshold(urlValue)) {
                const redirect = chrome.extension.getURL('blocked.html') + '?url=' + encodeURIComponent(url);

                chrome.tabs.update(tab.id, { url: redirect });
                return;
            }
        }
    })

    return true;
}

chrome.tabs.onCreated.addListener(function(tab) {
    run(tab);
});

chrome.tabs.onActivated.addListener(function(info) {
    chrome.tabs.get(info.tabId, function(tab) {
        run(tab);
    });
});

chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
    if (changeInfo.status === 'loading') {
        run(tab);
        return;
    }
});

init()

chrome.tabs.query({active: true, lastFocusedWindow: true}, tabs => {
    generateHtml(tabs[0]);
    // use `url` here inside the callback because it's asynchronous!
});