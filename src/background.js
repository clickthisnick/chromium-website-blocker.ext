function extractDomain(url) {
    return url.replace(/^(?:https?:\/\/)?(?:[^\/]+\.)?([^.\/]+\.[^.\/]+).*$/, "$1");
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

// function toggleUrl(url, inputText) {
//     console.log(`toggle ${url}`)

//     if (document.getElementById("input").value != inputText) {
//         console.log('Wrong Input Text')
//     } else {
//         let dateString = localStorage.getItem(url)
//         let counter = localStorage.getItem(unlockCounterVar)
//         let counterInt = Number(counter)
//         counterInt++
//         localStorage.setItem(unlockCounterVar, counterInt)

//         document.getElementById("counter").text = counterInt

//         if (isAboveThreshold(dateString)) {
//             localStorage.setItem(url, getMillisecondTime())
//             document.getElementById(url).value = "Enable"
//         } else {
//             localStorage.setItem(url, getMillisecondTime(millisecondsLimit))
//             document.getElementById(url).value = "Disable"
//         }
//     }
// }

function urlStartsWith(tabUrl) {
    for (let blockIdx = 0; blockIdx < blockedStartsWithUrl.length; blockIdx++) {
        let url = blockedStartsWithUrl[blockIdx];

        if (tabUrl.startsWith(url)) {
            return url;
        }
    }

    return false;
}

function regexMatch(tabUrl) {
    for (let blockIdx = 0; blockIdx < regexBlock.length; blockIdx++) {
        let url = regexBlock[blockIdx];

        // Regex match
        if (tabUrl.match(url) !== null) {
            return url;
        }
    }

    return false;
}

// function init() {
//     // Disable sites to begin with
//     const blockLists = blockedStartsWithUrl.concat(blockedDomains)

//     for(i = 0; i < blockLists.length; i++) {
//         let url = blockLists[i]

//         // set item in local storage
//         // local storage has string values
//         const millisecondsString = localStorage.getItem(url)
//         if (millisecondsString === null) {
//             localStorage.setItem(url, getMillisecondTime(millisecondsLimit))
//         }
//      }
// }

// function blockTime(match, tab) {
//     // Make sure its true in local storage
//     const urlValue = localStorage.getItem(match)

//     console.log(`blockTime - ${urlValue}`)

//     if (isAboveThreshold(urlValue) || urlValue === null) {
//         console.log(`should be blocking - ${urlValue}`)
//         return block(tab)
//     }
// }

async function blockIncognito(tab) {
    if (tab.url.startsWith('chrome')) {
        return
    }

    const redirect = chrome.runtime.getURL('blockedIncognito.html')

    await chrome.tabs.update(tab.id, { url: redirect });
}

async function block(tab) {
    const redirect = chrome.runtime.getURL('blocked.html') + '?url=' + encodeURIComponent(tab.url);
    console.log(`Blocked ${tab}`)
    await chrome.tabs.update(tab.id, { url: redirect });
}

async function blockAllTabs(tabs, tabIdNotTBlock) {
    tabs.forEach(async (tab) => {
        // Do not block urls with chrome in title
        if (tab.id !== tabIdNotTBlock && !tab.url.startsWith("chrome")) {
            await block(tab)
        }
    })
}

// function generateHtml(tab) {
//     // Generate html, but hide website names so you dont get influenced to click a different site
//     const div = document.getElementById('sites');

//     let url = tab.url.split('blocked.html?url=')
//     if (url.length === 1){
//         url = url[0]
//     } else {
//         url = url[1]
//     }

//     url = extractDomain(url)

//     const millisecondsString = localStorage.getItem(url)
//     const text = isAboveThreshold(millisecondsString) ? "Disable" : "Enable"
//     const enterText = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
//     div.innerHTML += "Enter This String:<br>"
//     for (i = 0; i < enterText.length; i++) {
//         div.innerHTML += `<span>${enterText[i]}</span>`
//     }
//     div.innerHTML += `<br><br>`
//     div.innerHTML += `<input id="input" type="input" value=""></input><br>`
//     div.innerHTML += `<input id="${url}" type="button" value="${text}"></input><br><br>`
//     div.innerHTML += `You've unlocked <span id="counter"></span> times today.<br><span id="counterWastedTime">`

//     // Set our timer counter
//     const unlockCounterString = localStorage.getItem(unlockCounterVar)
//     if (unlockCounterString === null) {
//         localStorage.setItem(unlockCounterVar, 0)
//         document.getElementById('counter').innerText = "0";
//     } else {
//         document.getElementById('counter').innerText = unlockCounterString;
//         document.getElementById('counterWastedTime').innerText = `Wasting ${Number(unlockCounterString) * 5} minutes`
//     }

//     document.getElementById(url).addEventListener("click", function(){toggleUrl(url, enterText)});
// }

async function run(tabs) {
    console.log('running tabs workflow')

    // Always remove any tabs that start with the chrome extensions so we dont end up in a weird spot
    let tabCount = tabs.length
    let tabIdx = 0

    while (tabIdx < tabCount -1) {
        let tab = tabs.pop()

        // Remove any incognito tabs
        // This is a way to circumvent the system
        if (tab.incognito) {
            await blockIncognito(tab)
            continue
        }

        if (!tab.url.startsWith("chrome")) {
            tabs.push(tab)
        }
        tabIdx += 1
    }

    // Highest priority, greedy
    for (i = 0; i < blockAllTabsIfUrlOpen.length; i++) {
        let url = blockAllTabsIfUrlOpen[i]
        for (x = 0; x < tabs.length; x++) {
            let tab = tabs[x]
            if (tab.url.startsWith(url)) {
                await blockAllTabs(tabs, tab.id)
            }
        }
    }

    // Remove any tabs from being blocked if they are always allowed
    alwaysAllowStartsWithUrl.forEach((allow) => {
        let tabCount = tabs.length
        let tabIdx = 0

        while (tabIdx < tabCount -1) {
            let tab = tabs.pop()
            if (!tab.url.startsWith(allow)) {
                tabs.push(tab)
            }
            tabIdx += 1
        }
    })

    tabs.forEach(async (tab) => {
        const tabDomain = extractDomain(tab.url)

        if (blockedDomains.includes(tabDomain)) {
            await block(tabDomain, tab)
        }

        let urlMatch = urlStartsWith(tab.url)

        if (urlMatch != false) {
            await block(urlMatch, tab)
        }

        let urlRegexMatch = regexMatch(tab.url)
        if (urlRegexMatch != false) {
            await block(urlRegexMatch, tab)
        }
    })
}

// chrome.tabs.onCreated.addListener(function(tab) {
//     console.log('tabs add listener')
//     chrome.tabs.getAllInWindow(tab.windowId, function(tabs) {
//         run(tabs)
//     })
// });

// chrome.tabs.onActivated.addListener(function(info) {
//     console.log('tabs get all windows')
//     chrome.tabs.get(info.tabId, function(tab) {
//         chrome.tabs.getAllInWindow(tab.windowId, function(tabs) {
//             run(tabs)
//         })
//     });
// });

// chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
//     console.log('tabs loading')
//     if (changeInfo.status === 'loading') {
//         chrome.tabs.getAllInWindow(tab.windowId, function(tabs) {
//             run(tabs)
//             return
//         })
//     }
// });

// // Block web requests
// var opt_extraInfoSpec = ["blocking", "requestHeaders"];
// chrome.webRequest.onBeforeSendHeaders.addListener(function(details) {
//     console.log('details')

//     console.log(`initiator ${details.initiator} - ${details.initiator in blockedRequestInitiator}`);
//     if (details.initiator in blockedRequestInitiator) {
//         return {'cancel': true}
//     }
//     return
// }, {urls: ["<all_urls>"]}, ['blocking', 'requestHeaders'])

// init()

// chrome.tabs.query({active: true, lastFocusedWindow: true}, tabs => {
//     console.log('query')

//     generateHtml(tabs[0]);
//     // use `url` here inside the callback because it's asynchronous!
// });

// function printTab(tabId) {
//     chrome.tabs.get(tabId, async (tab) => {
//       console.log(`Tab ${tab.id}`);
//     });
//   }


// async function move(activeInfo) {
//     console.log('tabs get all windows')
//     const queryOptions = { active: true, currentWindow: true };
//     const [tab] = await chrome.tabs.query(queryOptions);
//     await run([tab])
// }

async function move(activeInfo) {
    setTimeout(() => {
        console.log('tabs get all windows')
        chrome.tabs.query({"windowId": activeInfo.windowId}, async (tabs) => {
            await run(tabs)
        });
     }, 100);
}

// See https://developer.chrome.com/docs/extensions/reference/events/ for additional details.
chrome.tabs.onActivated.addListener(activeInfo => move(activeInfo));
chrome.tabs.onCreated.addListener(activeInfo => move(activeInfo));
chrome.tabs.onUpdated.addListener(activeInfo => move(activeInfo));
