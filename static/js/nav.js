

document.addEventListener("DOMContentLoaded",()=>{
    fetch("/api/profile")
    .then(res =>{
        if (res.status == 401){
            alert("Please Log in")
            return;
        }
        return res.json();
    })
    .then(user =>{
        let mail = document.querySelector(".email").innerHTML = user.email
        let user_name = document.querySelector(".name").innerHTML = user.name
    })
})

