function extractDomain(url) {
    return url.replace(/^(?:https?:\/\/)?(?:[^\/]+\.)?([^.\/]+\.[^.\/]+).*$/, "$1");
}

function redirect(tab) {
    const redirect_url = chrome.extension.getURL('blocked.html') + '?url=' + encodeURIComponent(tab.url);
    chrome.tabs.update(tab.id, { url: redirect_url });
}

function run(tab) {
    // Make a new tab go to redirect page
    if (tab.url == "chrome://newtab/") {
        redirect(tab)
        return;
    }

    // Skip any tab that is not on a url
    if (tab.url.search(/https?:/) !== 0) {
        return;
    };

    // Get the current domain of the tab
    const currentDomain = extractDomain(tab.url)
    const blockedList = [
        "news.ycombinator.com",
        "reddit.com",
        "youtube.com",
    ];

    blockedList.forEach((url) => {
        if (currentDomain === url) {
            redirect(tab)
            return;
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