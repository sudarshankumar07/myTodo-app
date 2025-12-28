login = document.querySelector(".login-btn")
login.addEventListener("click",()=>{
    window.location.href="/register_page"
})
let msg = document.querySelector(".none")
let msg1 = document.querySelector("#msg1")


signup = document.querySelector(".sign-btn")
signup.addEventListener("click",async()=>{
    const name = document.querySelector(".name").value;
    const email = document.querySelector(".email").value;
    const password = document.querySelector(".pass").value;

    if (!name || !email || !password){
        msg1.classList.add("msg1")
        msg1.classList.remove("none")
        return
    }

    const response = await fetch("/signup",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify({
            name:name,
            email:email,
            password:password
        })
    });
    const data = await response.json();
    if(data.success){
        window.location.href="/login_page"
    }else{
        msg.classList.add("msg")
        msg.classList.remove("none")
        msg1.classList.remove("msg1")
        msg1.classList.add("none")
    }


})
