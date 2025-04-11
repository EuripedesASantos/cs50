// Function to get cookies
import { getCookie } from './cookies.js';

document.addEventListener('DOMContentLoaded', function() {
    const divs = document.querySelectorAll('div[class="div_shipments"]');
        divs.forEach( div => {
            div.addEventListener('click', (event) => {Show(div);});
        });
});

function Show(node) {
    if (node.className === 'hide') {
        node.className='show';
        if (node.className === 'div_shipments') {node.title = 'Click to view all informations.'}
    } else {
        if (node.className === 'show') {node.className='hide';}
        if (node.className === 'div_shipments') {node.title = 'Click to hide informations.'}
    }
    if (node.hasChildNodes()) {node.childNodes.forEach( node => Show(node));}
}
