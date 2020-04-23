const tasks = [	
  'Do 10 push ups',	
  'Do 10 jumping jacks',	
  'Drink a glass of water',	
];	

const idx = Math.floor(Math.random() * tasks.length);	

document.getElementById('todo').innerHTML = tasks[idx];	
