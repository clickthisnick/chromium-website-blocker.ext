echo 'https://www.example.com' >> ../blockLists/alwaysAllowStartsWithUrl.txt
touch ../blockLists/blockAllTabsIfUrlOpen.txt
echo 'example.com' >> ../blockLists/blockedDomains.txt
echo 'https://www.example.com' >> ../blockLists/blockedStartsWithUrl.txt
echo 'https://duckduckgo.com/\\?q=foo\\+bar.*' >> ../blockLists/regexBlock.txt
echo 'https://www.example.com": "true' >> ../blockLists/blockedRequestInitiator.txt
