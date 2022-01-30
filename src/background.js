function extractDomain(url) {
  return url.replace(/^(?:https?:\/\/)?(?:[^\/]+\.)?([^.\/]+\.[^.\/]+).*$/, '$1');
}

function urlStartsWith(tabUrl) {
  for (let blockIdx = 0; blockIdx < blockedStartsWithUrl.length; blockIdx++) {
    const url = blockedStartsWithUrl[blockIdx];

    if (tabUrl.startsWith(url)) {
      return url;
    }
  }

  return false;
}

function regexMatch(tabUrl) {
  for (let blockIdx = 0; blockIdx < regexBlock.length; blockIdx++) {
    const url = regexBlock[blockIdx];

    // Regex match
    if (tabUrl.match(url) !== null) {
      return url;
    }
  }

  return false;
}

async function blockIncognito(tab) {
  if (tab.url.startsWith('chrome')) {
    return;
  }

  const redirect = chrome.runtime.getURL('blockedIncognito.html');

  await chrome.tabs.update(tab.id, {url: redirect});
}

async function block(tab) {
  const redirect = chrome.runtime.getURL('blocked.html') + '?url=' + encodeURIComponent(tab.url);
  console.log(`Blocked ${tab}`);
  await chrome.tabs.update(tab.id, {url: redirect});
}

async function blockAllTabs(tabs, tabIdNotTBlock) {
  tabs.forEach(async (tab) => {
    // Do not block urls with chrome in title
    if (tab.id !== tabIdNotTBlock && !tab.url.startsWith('chrome')) {
      await block(tab);
    }
  });
}

async function run(tabs) {
  // Always remove any tabs that start with the chrome extensions so we dont end up in a weird spot
  const tabCount = tabs.length;
  let tabIdx = 0;

  while (tabIdx < tabCount - 1) {
    const tab = tabs.pop();

    // Remove any incognito tabs
    // This is a way to circumvent the system
    if (tab.incognito) {
      await blockIncognito(tab);
      continue;
    }

    if (!tab.url.startsWith('chrome')) {
      tabs.push(tab);
    }
    tabIdx += 1;
  }

  // Highest priority, greedy
  for (i = 0; i < blockAllTabsIfUrlOpen.length; i++) {
    const url = blockAllTabsIfUrlOpen[i];
    for (x = 0; x < tabs.length; x++) {
      const tab = tabs[x];
      if (tab.url.startsWith(url)) {
        await blockAllTabs(tabs, tab.id);
      }
    }
  }

  // Remove any tabs from being blocked if they are always allowed
  alwaysAllowStartsWithUrl.forEach((allow) => {
    const tabCount = tabs.length;
    let tabIdx = 0;

    while (tabIdx < tabCount - 1) {
      const tab = tabs.pop();
      if (!tab.url.startsWith(allow)) {
        tabs.push(tab);
      }
      tabIdx += 1;
    }
  });

  tabs.forEach(async (tab) => {
    const tabDomain = extractDomain(tab.url);

    if (blockedDomains.includes(tabDomain)) {
      await block(tabDomain, tab);
    }

    const urlMatch = urlStartsWith(tab.url);
    if (urlMatch != false) {
      await block(urlMatch, tab);
    }

    const urlRegexMatch = regexMatch(tab.url);
    if (urlRegexMatch != false) {
      await block(urlRegexMatch, tab);
    }
  });
}

async function move(activeInfo) {
  setTimeout(() => {
    chrome.tabs.query({'windowId': activeInfo.windowId}, async (tabs) => {
      await run(tabs);
    });
  }, 100);
}

// See https://developer.chrome.com/docs/extensions/reference/events/ for additional details.
chrome.tabs.onActivated.addListener((activeInfo) => move(activeInfo));
chrome.tabs.onCreated.addListener((activeInfo) => move(activeInfo));
chrome.tabs.onUpdated.addListener((activeInfo) => move(activeInfo));
