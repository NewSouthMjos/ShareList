/* code from https://htmlacademy.ru/demos/65 */

const tasksListElement = document.querySelector(`.tasks__list`);
const taskElements = tasksListElement.querySelectorAll(`.tasks__item`);


for (const task of taskElements) {
  task.draggable = true;
}


tasksListElement.addEventListener(`dragstart`, (evt) => {
  evt.target.classList.add(`selected`);
});

tasksListElement.addEventListener(`dragend`, (evt) => {
  evt.target.classList.remove(`selected`);
});

const getNextElement = () => {
    // Пока поставим заглушку
  const nextElement = null;
  
  return nextElement;
};

tasksListElement.addEventListener(`dragover`, (evt) => {
  evt.preventDefault();
  
  const activeElement = tasksListElement.querySelector(`.selected`);
  const currentElement = evt.target;
  const isMoveable = activeElement !== currentElement &&
    currentElement.classList.contains(`tasks__item`);
    
  if (!isMoveable) {
    return;
  }
  
  const nextElement = (currentElement === activeElement.nextElementSibling) ?
		currentElement.nextElementSibling :
		currentElement;
		
	tasksListElement.insertBefore(activeElement, nextElement);
	//changind order id:
  //activeElement.value = "30"
  number_items_in_order();
  //inner_order_input = activeElement.children[0]
  /* if (inner_order_input.value === "2") {
    inner_order_input.value = "50";
  } */
});

function number_items_in_order() {
  taskElements_2 = tasksListElement.querySelectorAll(`.tasks__item`);
  let i = 1;
  for (task of taskElements_2) {
	task.children[0].value = i;
	i++;
}
}