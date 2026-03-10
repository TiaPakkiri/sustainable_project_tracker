function filterProjects() {
  const searchValue = document.getElementById("searchInput").value.toLowerCase();
  const campusValue = document.getElementById("campusFilter").value.toLowerCase();
  const categoryValue = document.getElementById("categoryFilter").value.toLowerCase();
  const statusValue = document.getElementById("statusFilter").value.toLowerCase();

  const projects = document.querySelectorAll(".project-card");

  projects.forEach(project => {
    const title = project.dataset.title.toLowerCase();
    const campus = project.dataset.campus.toLowerCase();
    const category = project.dataset.category.toLowerCase();
    const status = project.dataset.status.toLowerCase();

    const matchesSearch = title.includes(searchValue);
    const matchesCampus = campusValue === "" || campus === campusValue;
    const matchesCategory = categoryValue === "" || category === categoryValue;
    const matchesStatus = statusValue === "" || status === statusValue;

    if (matchesSearch && matchesCampus && matchesCategory && matchesStatus) {
      project.style.display = "block";
    } else {
      project.style.display = "none";
    }
  });
}

function resetFilters() {
  document.getElementById("searchInput").value = "";
  document.getElementById("campusFilter").value = "";
  document.getElementById("categoryFilter").value = "";
  document.getElementById("statusFilter").value = "";
  filterProjects();
}
