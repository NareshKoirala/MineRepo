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
    console.log(stars);
}