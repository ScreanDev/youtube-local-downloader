// Variables à initialiser
const allElements = document.querySelector("*");
const mouseDot = document.querySelector(".mouse-dot");
const navCategories = document.querySelector("nav.categories");
const blurBox = document.querySelector(".blur-bg");
const bodyContainer = document.querySelector("body")

const toolWindowShowcaseHeaderBG = document.querySelector("#tool_window_showcase_header_background")
const creditsContainer = document.querySelector("#credits-container")
const headerCategoriesIcon = document.querySelector("#header-categories-icon")

let popupStatus = 0


navCategories.style.marginTop="-20px";
navCategories.style.opacity="0.8";

window.addEventListener("scroll", () => {
    if (window.scrollY > 300) {
        navCategories.style.marginTop="0px";
        navCategories.style.opacity="1";
        navCategories.style.borderRadius="0%";
        navCategories.style.height="6%";
        navCategories.style.left="0px";
        navCategories.style.top="0px";
        navCategories.style.width="200vh";
        headerCategoriesIcon.style.display="flex";
    } else {
        navCategories.style.marginTop="-20px";
        navCategories.style.opacity="0.8";
        navCategories.style.borderRadius="100px";
        navCategories.style.height="6%";
        navCategories.style.left="180px";
        navCategories.style.top="70px";
        navCategories.style.width="100vh";
        headerCategoriesIcon.style.display="None";
    }
});

/*window.addEventListener("scroll", () => {
    if (window.scrollY > 300) {
        navCategories.style.marginTop="0px";
        navCategories.style.opacity="1";
    } else {
        navCategories.style.marginTop="-100px";
        navCategories.style.opacity="0";
    }
});*/

function togglePopup(){
    let discordPopup = document.querySelector(".discord-pop-up");
    let popupCloseText = document.querySelector(".pop-up-close-info")
    discordPopup.classList.toggle("active");
    popupCloseText.classList.toggle("active");
    if (popupStatus === 0) {
        blurBox.style.opacity="1";
        blurBox.style.pointerEvents="all";
        bodyContainer.style.overflowY="hidden";
        popupStatus = 1
    } else {
        blurBox.style.opacity="0";
        blurBox.style.pointerEvents="none";
        bodyContainer.style.overflowY="scroll";
        popupStatus = 0
    }
}

function shakeToolWinShowcaseBG(){
    let toolWindowShowcaseHeaderPosY = Math.sin(Date.now()/1000)*2;
    let toolWindowShowcaseHeaderRotate = Math.sin(Date.now()/3000)*4;
    toolWindowShowcaseHeaderBG.style.top = `${-28 + toolWindowShowcaseHeaderPosY}vh`;
    toolWindowShowcaseHeaderBG.style.rotate = `${5 + toolWindowShowcaseHeaderRotate}deg`;
    requestAnimationFrame(shakeToolWinShowcaseBG);
}


function adaptCreditsContainer(){
    if (window.scrollY > 300) {
        creditsContainer.style.top="150px";
    } else {
        creditsContainer.style.top="40px";
    }
    requestAnimationFrame(adaptCreditsContainer);
}




// FONCTION À MODIFIER CAR NON FONCTIONNELLE
fetch('../version.txt')
    .then(response => response.text())
    .then(data => {
      // Mettre à jour le texte avec la version récupérée
      document.getElementById('tool-version').innerText = `Version ${data.trim()}`;
    })
    .catch(error => console.error('Erreur lors de la récupération de la version :', error));


adaptCreditsContainer();
shakeToolWinShowcaseBG();

/*window.addEventListener("mousemove", (e) => {
    console.log(e)
    const x = e.pageX;
    const y = e.pageY;

    mouseDot.style.left = x - 25 + "px";
    mouseDot.style.top = y - 25 + "px";
});*/