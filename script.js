fetch("https://my-fastapi.onrender.com/clicks")  // Replace with your FastAPI URL
  .then(response => response.json())
  .then(data => {
      console.log("Click data:", data);
      document.getElementById("clicks").innerHTML = JSON.stringify(data, null, 2);
  })
  .catch(error => console.error("Error fetching data:", error));
