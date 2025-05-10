$(document).ready(function() {
  // Dark mode toggle
  const darkModeSwitch = document.getElementById('darkModeSwitch');
  
  // Check for saved dark mode preference
  if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
    darkModeSwitch.checked = true;
  }
  
  // Handle dark mode toggle
  darkModeSwitch.addEventListener('change', function() {
    if (this.checked) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('darkMode', 'true');
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('darkMode', 'false');
    }
  });
  
  // Fetch component data
  fetch('data.json')
    .then(response => response.json())
    .then(data => {
      // Update last updated timestamp
      document.getElementById('last-updated').innerHTML = 
        `<i class="bi bi-clock me-1"></i> Last Updated: ${data.generated_date}`;
      
      // Clear loading message
      const tableBody = document.getElementById('tableBody');
      tableBody.innerHTML = '';
      
      // Populate table with data
      data.components.forEach(component => {
        const row = document.createElement('tr');
        
        // Component name cell
        const nameCell = document.createElement('td');
        nameCell.innerHTML = `<strong>${component.name}</strong>`;
        row.appendChild(nameCell);
        
        // Description cell
        const descCell = document.createElement('td');
        descCell.textContent = component.description;
        row.appendChild(descCell);
        
        // Helm version cell
        const helmVersionCell = document.createElement('td');
        helmVersionCell.textContent = component.helm_version;
        row.appendChild(helmVersionCell);
        
        // App version cell
        const appVersionCell = document.createElement('td');
        appVersionCell.textContent = component.app_version;
        row.appendChild(appVersionCell);
        
        // GitHub release cell
        const githubReleaseCell = document.createElement('td');
        const githubLink = document.createElement('a');
        githubLink.href = component.github_url;
        githubLink.target = '_blank';
        githubLink.textContent = component.github_release;
        githubLink.className = 'github-link';
        githubReleaseCell.appendChild(githubLink);
        row.appendChild(githubReleaseCell);
        
        // Release date cell
        const dateCell = document.createElement('td');
        dateCell.className = 'version-date';
        dateCell.textContent = component.github_date;
        row.appendChild(dateCell);
        
        tableBody.appendChild(row);
      });
      
      // Initialize DataTable
      $('#versionsTable').DataTable({
        paging: false,
        responsive: true,
        order: [[0, 'asc']],
        language: {
          search: "Filter components:"
        }
      });
    })
    .catch(error => {
      console.error('Error fetching data:', error);
      document.getElementById('tableBody').innerHTML = 
        `<tr><td colspan="6" class="text-center text-danger">
          Error loading data. Please try again later.
        </td></tr>`;
    });
});
