$(document).ready(()=>{
    console.log("Here its Ready For JS");

    AddStars();


});

const numDots = 100; // Adjust as needed

function AddStars()
{
    for (let i = 0; i < numDots; i++) 
    {
        // Generate random positions
        const randomX = Math.floor(Math.random() * $(window).width());
        const randomY = Math.floor(Math.random() * $(window).height());


        // Create and style the dot
        $('<div>').css({
            width: '3px',            // Size of the dot
            height: '3px',
            backgroundColor: 'white', // Color
            borderRadius: '50%',     // Circular shape
            position: 'absolute',    // Absolute positioning
            top: `${randomY}px`,     // Random Y position
            left: `${randomX}px`,    // Random X position
            margin: '0'              // Remove margin for precise positioning
        }).appendTo('body');
    }
}