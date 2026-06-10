let lastUpdatedAgo = document.getElementById("last-updated-ago");
let lastUpdatedTs = document.getElementById("last-updated-ts");

lastUpdatedTs.textContent = window.lastUpdated.toLocaleString();

function updateLastUpdatedAgo() {
    // diff window.lastUpdated and now in ms
    let diff = Date.now() - window.lastUpdated.getTime();
    lastUpdatedAgo.textContent = diff.toString();
    requestAnimationFrame(updateLastUpdatedAgo);
}
updateLastUpdatedAgo();
