/**
 * Neuro-Symbolic University QA Visualizer
 * Main Application JavaScript
 * 
 * Features:
 * - Interactive knowledge graph with Cytoscape.js
 * - Animated step-by-step reasoning trace
 * - Node filtering and details modal
 */

// ============================================================
// Global State
// ============================================================
let cy = null;  // Cytoscape instance
let graphData = { nodes: [], edges: [] };

// ============================================================
// API Functions
// ============================================================

async function fetchGraph() {
    try {
        const response = await fetch('/api/graph');
        if (!response.ok) throw new Error('Failed to fetch graph');
        return await response.json();
    } catch (error) {
        console.error('Error fetching graph:', error);
        return { nodes: [], edges: [] };
    }
}

async function fetchExamples() {
    try {
        const response = await fetch('/api/examples');
        if (!response.ok) throw new Error('Failed to fetch examples');
        return await response.json();
    } catch (error) {
        console.error('Error fetching examples:', error);
        return { examples: [] };
    }
}

async function submitQuery(question) {
    const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
    });
    if (!response.ok) throw new Error('Query failed');
    return await response.json();
}

// ============================================================
// Cytoscape Graph Setup
// ============================================================

function initializeGraph(data) {
    graphData = data;

    cy = cytoscape({
        container: document.getElementById('cy-container'),
        elements: [...data.nodes, ...data.edges],
        style: [
            // Base node style
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'font-size': '10px',
                    'color': '#ffffff',
                    'text-outline-color': '#000',
                    'text-outline-width': 2,
                    'text-max-width': '100px',
                    'text-wrap': 'wrap',
                    'min-zoomed-font-size': 8
                }
            },
            // Department nodes
            {
                selector: 'node[type="department"]',
                style: {
                    'background-color': '#3b82f6',
                    'shape': 'roundrectangle',
                    'width': 80,
                    'height': 40,
                    'font-weight': 'bold'
                }
            },
            // Faculty nodes
            {
                selector: 'node[type="faculty"]',
                style: {
                    'background-color': '#22c55e',
                    'shape': 'ellipse',
                    'width': 60,
                    'height': 60
                }
            },
            // Course nodes
            {
                selector: 'node[type="course"]',
                style: {
                    'background-color': '#f59e0b',
                    'shape': 'roundrectangle',
                    'width': 100,
                    'height': 35,
                    'font-size': '9px'
                }
            },
            // Edge styles
            {
                selector: 'edge',
                style: {
                    'width': 1.5,
                    'line-color': 'rgba(255, 255, 255, 0.2)',
                    'target-arrow-color': 'rgba(255, 255, 255, 0.2)',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier'
                }
            },
            // Prerequisite edges
            {
                selector: 'edge[relation="prerequisite"]',
                style: {
                    'width': 2.5,
                    'line-color': '#f87171',
                    'target-arrow-color': '#f87171',
                    'line-style': 'solid'
                }
            },
            // Teaches edges
            {
                selector: 'edge[relation="teaches"]',
                style: {
                    'line-color': '#22c55e',
                    'target-arrow-color': '#22c55e',
                    'line-style': 'dashed'
                }
            },
            // Heads edges
            {
                selector: 'edge[relation="heads"]',
                style: {
                    'line-color': '#a855f7',
                    'target-arrow-color': '#a855f7',
                    'width': 3
                }
            },
            // Highlighted state
            {
                selector: '.highlighted',
                style: {
                    'background-color': '#fbbf24',
                    'border-width': 4,
                    'border-color': '#ffffff',
                    'z-index': 999
                }
            },
            {
                selector: 'edge.highlighted',
                style: {
                    'line-color': '#fbbf24',
                    'target-arrow-color': '#fbbf24',
                    'width': 4,
                    'z-index': 999
                }
            },
            // Hidden state
            {
                selector: '.hidden',
                style: {
                    'display': 'none'
                }
            }
        ],
        layout: {
            name: 'cose-bilkent',
            animate: false,
            nodeDimensionsIncludeLabels: true,
            idealEdgeLength: 100,
            nodeRepulsion: 4500,
            gravity: 0.25,
            numIter: 2500,
            tile: true
        },
        // Interaction options
        minZoom: 0.3,
        maxZoom: 3,
        wheelSensitivity: 0.3
    });

    // Click handler for nodes
    cy.on('tap', 'node', function (evt) {
        showNodeDetails(evt.target.data());
    });

    // Hover effects
    cy.on('mouseover', 'node', function (evt) {
        const node = evt.target;
        node.addClass('hover');
        // Highlight connected edges
        node.connectedEdges().addClass('hover-edge');
    });

    cy.on('mouseout', 'node', function (evt) {
        const node = evt.target;
        node.removeClass('hover');
        node.connectedEdges().removeClass('hover-edge');
    });
}

// ============================================================
// Node Details Modal
// ============================================================

function showNodeDetails(data) {
    const modal = document.getElementById('node-modal');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');

    let content = '';

    if (data.type === 'department') {
        title.textContent = `🏛️ ${data.label}`;
        content = `
            <p><strong>Code:</strong> ${data.code}</p>
            <p><strong>Type:</strong> Department</p>
        `;
    } else if (data.type === 'faculty') {
        title.textContent = `👨‍🏫 ${data.label}`;
        content = `
            <p><strong>Title:</strong> ${data.title || 'N/A'}</p>
            <p><strong>Email:</strong> ${data.email || 'N/A'}</p>
            <p><strong>Research Areas:</strong></p>
            <ul>
                ${(data.research_areas || []).map(a => `<li>${a}</li>`).join('') || '<li>None listed</li>'}
            </ul>
        `;
    } else if (data.type === 'course') {
        title.textContent = `📚 ${data.code}`;
        content = `
            <p><strong>Name:</strong> ${data.name}</p>
            <p><strong>Credits:</strong> ${data.credits}</p>
            <p><strong>Level:</strong> ${data.level}</p>
            <p><strong>Description:</strong> ${data.description || 'No description'}</p>
        `;
    }

    body.innerHTML = content;
    modal.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('node-modal').classList.add('hidden');
}

// ============================================================
// Query Processing & Reasoning Animation
// ============================================================

async function handleQuery() {
    const questionInput = document.getElementById('question-input');
    const question = questionInput.value.trim();

    if (!question) return;

    // Show loading
    showLoading(true);
    clearReasoningAndAnswer();

    try {
        const result = await submitQuery(question);

        // Hide loading
        showLoading(false);

        // Animate reasoning steps
        await animateReasoningSteps(result.reasoning_steps);

        // Show answer
        displayAnswer(result);

    } catch (error) {
        showLoading(false);
        displayError(error.message);
    }
}

async function animateReasoningSteps(steps) {
    const container = document.getElementById('reasoning-container');
    container.innerHTML = '';

    // Clear any previous highlights
    cy.elements().removeClass('highlighted');

    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];

        // Create step element
        const stepEl = document.createElement('div');
        stepEl.className = 'reasoning-step';
        stepEl.style.animationDelay = `${i * 0.1}s`;

        stepEl.innerHTML = `
            <span class="step-number">${step.step_number}</span>
            <div class="step-content">
                <div class="step-rule">${step.rule_name}</div>
                <div class="step-description">${step.description}</div>
            </div>
        `;

        container.appendChild(stepEl);

        // Highlight relevant nodes in graph
        highlightNodesForStep(step);

        // Wait before showing next step
        await sleep(500);
    }
}

function highlightNodesForStep(step) {
    // Try to find and highlight relevant nodes based on step content
    const description = step.description.toLowerCase();

    // Look for course codes
    const courseCodeMatch = description.match(/[a-z]{2,4}\d{3}/gi);
    if (courseCodeMatch) {
        courseCodeMatch.forEach(code => {
            const node = cy.nodes().filter(n =>
                n.data('code')?.toUpperCase() === code.toUpperCase()
            );
            if (node.length) {
                node.addClass('highlighted');
            }
        });
    }

    // Look for faculty names
    if (step.rule_name.includes('FACULTY') || description.includes('faculty')) {
        cy.nodes('[type="faculty"]').addClass('highlighted');
    }

    // Look for department references
    if (step.rule_name.includes('DEPARTMENT') || description.includes('department')) {
        cy.nodes('[type="department"]').addClass('highlighted');
    }
}

function displayAnswer(result) {
    const container = document.getElementById('answer-container');

    if (!result.success) {
        container.innerHTML = `<div class="error-message">${result.error || 'Unknown error'}</div>`;
        return;
    }

    container.innerHTML = `<div class="answer-text">${formatAnswer(result.answer)}</div>`;
}

function formatAnswer(answer) {
    // Simple markdown-like formatting
    return answer
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/- /g, '• ');
}

function displayError(message) {
    const container = document.getElementById('answer-container');
    container.innerHTML = `<div class="error-message">❌ ${message}</div>`;
}

function clearReasoningAndAnswer() {
    document.getElementById('reasoning-container').innerHTML =
        '<p class="placeholder-text">Processing your question...</p>';
    document.getElementById('answer-container').innerHTML = '';
    cy.elements().removeClass('highlighted');
}

// ============================================================
// Utility Functions
// ============================================================

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

// ============================================================
// Filter Controls
// ============================================================

function setupFilters() {
    const filters = ['dept', 'faculty', 'course'];

    filters.forEach(type => {
        const checkbox = document.getElementById(`filter-${type}`);
        if (checkbox) {
            checkbox.addEventListener('change', () => {
                const fullType = type === 'dept' ? 'department' : type;
                const nodes = cy.nodes(`[type="${fullType}"]`);

                if (checkbox.checked) {
                    nodes.removeClass('hidden');
                } else {
                    nodes.addClass('hidden');
                }
            });
        }
    });
}

// ============================================================
// Example Questions Dropdown
// ============================================================

async function setupExamples() {
    const select = document.getElementById('example-select');
    const { examples } = await fetchExamples();

    examples.forEach(ex => {
        const option = document.createElement('option');
        option.value = ex.question;
        option.textContent = `[${ex.category}] ${ex.question}`;
        select.appendChild(option);
    });

    select.addEventListener('change', () => {
        if (select.value) {
            document.getElementById('question-input').value = select.value;
        }
    });
}

// ============================================================
// Event Listeners
// ============================================================

function setupEventListeners() {
    // Ask button
    document.getElementById('btn-ask').addEventListener('click', handleQuery);

    // Enter key in textarea
    document.getElementById('question-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleQuery();
        }
    });

    // Modal close
    document.getElementById('modal-close').addEventListener('click', closeModal);
    document.getElementById('node-modal').addEventListener('click', (e) => {
        if (e.target.id === 'node-modal') closeModal();
    });

    // Graph controls
    document.getElementById('btn-reset-view').addEventListener('click', () => {
        cy.reset();
    });

    document.getElementById('btn-fit').addEventListener('click', () => {
        cy.fit(null, 50);
    });
}

// ============================================================
// Initialize Application
// ============================================================

async function init() {
    showLoading(true);

    try {
        // Fetch graph data
        const graphData = await fetchGraph();

        // Initialize Cytoscape
        initializeGraph(graphData);

        // Setup UI components
        setupFilters();
        setupEventListeners();
        await setupExamples();

    } catch (error) {
        console.error('Initialization error:', error);
    } finally {
        showLoading(false);
    }
}

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', init);
