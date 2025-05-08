$(document).ready(() => {
    console.log("Here its Ready For JS");
    AddStars();
});

const numDots = 10;
let stars = [];

function AddStars() {
    for (let i = 0; i < numDots; i++) {
        const randomX = Math.floor(Math.random() * $(window).width());
        const randomY = Math.floor(Math.random() * $(window).height());

        let star = $('<span>').addClass('star').css({
            top: `${randomY}px`,
            left: `${randomX}px`,
        });

        star.appendTo('body');

        stars.push(star);
    }

    for (let i = 0; i < numDots * 30; i++) {
        const randomX = Math.floor(Math.random() * $(window).width());
        const randomY = Math.floor(Math.random() * $(window).height());
        const randomDelay = Math.random() * 20; // Random delay between 0 and 2 seconds
        const randomDuration = 1 + Math.random() * 9; // Random duration between 1 and 3 seconds
    
        let dot = $('<div>').addClass('blink').css({
            top: `${randomY}px`,
            left: `${randomX}px`,
            'animation-delay': `${randomDelay}s`,
            'animation-duration': `${randomDuration}s`
        });
    
        dot.appendTo('body');
        stars.push(dot);
    }

}