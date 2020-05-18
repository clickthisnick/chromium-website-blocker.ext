function extractDomain(url) {
    return url.replace(/^(?:https?:\/\/)?(?:[^\/]+\.)?([^.\/]+\.[^.\/]+).*$/, "$1");
}

// List of domains to block
const blockedList = [
    "example.com",
]

function toggleUrl(url) {
    console.log(`toggle ${url}`)

    let boolString = localStorage.getItem(url)
    if (boolString === 'true') {
        document.getElementById(url).value = "Enable"
        localStorage.setItem(url, 'false')
    } else {
        localStorage.setItem(url, 'true')
        document.getElementById(url).value = "Disable"
    }
}

function init() {
    const handlers = {}
    let div = document.getElementById('sites');

    for(i = 0; i < blockedList.length; i++) {
        let url = blockedList[i]

        // set item in local storage
        // local storage has string values
        const boolString = localStorage.getItem(url)
        if (boolString === null) {
            localStorage.setItem(url, "true")
        } else {
            const text = boolString === "true" ? "Disable" : "Enable"
            div.innerHTML += "<br>"
            div.innerHTML += "<br>"
            div.innerHTML += url
            div.innerHTML += `<input id="${url}" type="button" value="${text}"></input>`

        }
    }

    for(i = 0; i < blockedList.length; i++) {
        let url = blockedList[i]

        const boolString = localStorage.getItem(url)

        if (boolString !== null) {
            handlers[url] = document.getElementById(url);
            handlers[url].addEventListener("click", function(){toggleUrl(url)});
        }
    }
 
    console.log(handlers)
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

            if (urlValue !== "false") {
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