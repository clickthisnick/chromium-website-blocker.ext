function extractDomain(url) {
    return url.replace(/^(?:https?:\/\/)?(?:[^\/]+\.)?([^.\/]+\.[^.\/]+).*$/, "$1");
}

// List of domains to block
const blockedList = [
    "example.com",
]

function toggleUrl(url) {
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
    const div = document.getElementById('sites');
    blockedList.forEach((url) => {

        // set item in local storage
        // local storage has string values
        const boolString = localStorage.getItem(url)
        if (boolString === null) {
            localStorage.setItem(url, "true")
        }

        const text = boolString === "true" ? "Disable" : "Enable"

        div.innerHTML += "<br>"
        div.innerHTML += url
        div.innerHTML += `<input id="${url}" type="button" value="${text}" />`

        let btn1 = document.getElementById(url);
        btn1.addEventListener("click", function(){toggleUrl(url)});
    })
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

            if (urlValue !== null && urlValue !== "false") {
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