// Define the navigation structure
const navigationLinks = [
    { 
        title: 'Metro',
        type: 'dropdown',
        items: [
            { title: 'Profiles', path: '/location/location.html' },
            { title: 'Denver', path: '/location/map/denver.html' },
            { title: 'Phoenix', path: '/location/map/phoenix.html' },
            { title: 'Minneapolis', path: '/location/map/minneapolis.html' }
        ]
    },
    { 
        title: 'Housing',
        type: 'dropdown',
        items: [
            { title: 'Rentals', path: '/residence/rent/rent.html' },
            { title: 'For Sale', path: '/residence/own/own.html' },
        ]
    },
    { 
        title: 'Work',
        type: 'dropdown',
        items: [
            { title: 'Jobs', path: '/job/job.html' },
            { title: 'Facilities', path: '/employer/facility/facility.html' },
            { title: 'Employers', path: '/employer/employer.html' },
        ]
    },
    // Add the News link
    { 
        title: 'News',
        type: 'link',
        path: '/shared/news.html'
    },
];

// Auto-detect environment and set path prefix
const PATH_PREFIX = window.location.hostname === 'majway27.github.io' ? '/moving' : '';

function createNavigation() {
    const nav = document.createElement('nav');
    nav.className = 'navbar navbar-expand-lg navbar-dark bg-primary';
    
    const container = document.createElement('div');
    container.className = 'container-fluid';
    
    // Create brand link
    const brand = document.createElement('a');
    brand.className = 'navbar-brand';
    brand.href = getRelativePath('/index.html');
    brand.textContent = 'Relocation Planner';
    
    // Create toggle button for mobile
    const toggleButton = document.createElement('button');
    toggleButton.className = 'navbar-toggler';
    toggleButton.type = 'button';
    toggleButton.setAttribute('data-bs-toggle', 'collapse');
    toggleButton.setAttribute('data-bs-target', '#navbarNav');
    toggleButton.innerHTML = '<span class="navbar-toggler-icon"></span>';
    
    // Create collapsible navigation content
    const navContent = document.createElement('div');
    navContent.className = 'collapse navbar-collapse justify-content-center';
    navContent.id = 'navbarNav';
    
    const ul = document.createElement('ul');
    ul.className = 'navbar-nav';
    
    // Get the current page path
    const currentPath = window.location.pathname;
    
    // Create navigation items
    navigationLinks.forEach(link => {
        const li = document.createElement('li');
        li.className = 'nav-item';
        
        if (link.type === 'dropdown') {
            li.className += ' dropdown';
            const a = document.createElement('a');
            a.className = 'nav-link dropdown-toggle';
            a.href = '#';
            a.role = 'button';
            a.setAttribute('data-bs-toggle', 'dropdown');
            a.textContent = link.title;
            
            const dropdownMenu = document.createElement('ul');
            dropdownMenu.className = 'dropdown-menu';
            
            link.items.forEach(item => {
                const dropdownItem = document.createElement('li');
                const itemLink = document.createElement('a');
                itemLink.className = 'dropdown-item';
                if (currentPath.endsWith(item.path)) {
                    itemLink.className += ' active';
                }
                itemLink.href = getRelativePath(item.path);
                itemLink.textContent = item.title;
                dropdownItem.appendChild(itemLink);
                dropdownMenu.appendChild(dropdownItem);
            });
            
            li.appendChild(a);
            li.appendChild(dropdownMenu);
        } else {
            const a = document.createElement('a');
            a.className = 'nav-link';
            if (currentPath.endsWith(link.path)) {
                a.className += ' active';
            }
            a.href = getRelativePath(link.path);
            a.textContent = link.title;
            li.appendChild(a);
        }
        
        ul.appendChild(li);
    });
    
    navContent.appendChild(ul);
    container.appendChild(brand);
    container.appendChild(toggleButton);
    container.appendChild(navContent);
    nav.appendChild(container);
    
    return nav;
}

// Helper function to calculate relative path based on current page depth
function getRelativePath(targetPath) {
    const currentPath = window.location.pathname;
    // Remove the production path prefix if it exists
    const relativePath = currentPath.replace(PATH_PREFIX, '');
    
    // If it's the home link, calculate path to root
    if (targetPath === '/index.html') {
        // Count the number of directory levels, ensuring it's at least 0
        const depth = Math.max(0, (relativePath.match(/\//g) || []).length - 1);
        return depth === 0 ? 'index.html' : '../'.repeat(depth) + 'index.html';
    }

    // Calculate the current directory depth
    const currentParts = relativePath.split('/').filter(Boolean);
    // Remove the filename from the count
    const currentDepth = Math.max(0, currentParts.length - 1);
    
    // Calculate relative path prefix
    const prefix = currentDepth === 0 ? '' : '../'.repeat(currentDepth);
    return prefix + targetPath.replace(/^\//, '');
}

// Function to initialize navigation
function initNavigation() {
    const nav = createNavigation();
    const firstElement = document.body.firstChild;
    document.body.insertBefore(nav, firstElement);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initNavigation); 