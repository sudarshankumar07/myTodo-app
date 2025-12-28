// btn = document.getElementById("btn");
// btn.addEventListener("click",()=>{
//     fetch("api/data",{
//         method:"POST",
//         headers:{
//             "Content-Type":"application/json"

//         },
//         body:JSON.stringify({name:"sudarshan"})
//     })
//     .then(res=>res.json())
//     .then(data=>{
//         console.log(data.message);
//     })
//     .catch(err=>console.error(err))
// })
login = document.querySelector(".log")
register = document.querySelector(".reg")
login.addEventListener("click",()=>callAPI("/api/login"))
register.addEventListener("click",()=>callAPI("/api/register"))
function callAPI(url){
    fetch(url,{method:"POST"})
    .then(res => res.json())
    .then(data=>{
        if(data.success){
            window.location.href = data.redirect;
        }
    })
    .catch(err=>console.error(err))
}