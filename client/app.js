document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const submitBtn = document.getElementById('submit-btn');
    const chatMessages = document.getElementById('chat-messages');
    const responseContainer = document.getElementById('response-container');
    const responseData = document.getElementById('response-data');
    const loader = document.getElementById('loader');
    const statusElem = document.getElementById('status');
    const filePathElem = document.getElementById('file-path');
    const sqlPromptInput = document.getElementById('sql-prompt');
    const chartTypeSelect = document.getElementById('chart-type');
    const artifactPlaceholder = document.getElementById('artifact-placeholder');
    const artifactContent = document.getElementById('artifact-content');
    const artifactFrame = document.getElementById('artifact-frame');
    const closeArtifactBtn = document.getElementById('close-artifact');
    const artifactContainer = document.getElementById('artifact-container');
    const resizeBtn = document.getElementById('resize-artifact');
    
    // Add initial event listeners
    submitBtn.addEventListener('click', handleSubmit);
    sqlPromptInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSubmit();
        }
    });
    
    closeArtifactBtn.addEventListener('click', function() {
        artifactContent.classList.add('hidden');
        artifactPlaceholder.classList.remove('hidden');
    });
    
    // Add resize button functionality
    resizeBtn.addEventListener('click', function() {
        artifactContainer.classList.toggle('fullscreen');
        
        // Update the resize button icon based on state
        if (artifactContainer.classList.contains('fullscreen')) {
            resizeBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"></path>
                </svg>
            `;
        } else {
            resizeBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"></path>
                </svg>
            `;
        }
    });
    
    // Main submit handler function
    function handleSubmit() {
        const sqlPrompt = sqlPromptInput.value.trim();
        const chartType = chartTypeSelect.value;
        
        if (!sqlPrompt) {
            addMessage('Please enter an SQL prompt', 'system');
            return;
        }
        
        // Add user message to chat
        addMessage(`SQL Query: ${sqlPrompt}\nChart Type: ${chartType}`, 'user');
        
        // Clear the input box after submission
        sqlPromptInput.value = '';
        
        // Show loader in response section
        responseContainer.classList.remove('hidden');
        loader.classList.remove('hidden');
        responseData.classList.add('hidden');
        
        // Add system message indicating processing
        addMessage('Processing your request...', 'system');
        
        // Prepare the request data
        const requestData = {
            sql_prompt: sqlPrompt,
            chart_type: chartType
        };
        
        // Make the API call
        fetch('http://127.0.0.1:8000/api/v1/analysis/analyse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide loader and show response data
            loader.classList.add('hidden');
            responseData.classList.remove('hidden');
            
            // Update UI with response data
            statusElem.textContent = data.status;
            filePathElem.textContent = extractFilename(data.file_path);
            
            // Format explanation for markdown and add to chat
            const formattedExplanation = formatMarkdown(data.explanation);
            addMessage(`### Analysis complete!\n\n${formattedExplanation}`, 'system');
            
            // Automatically display the artifact without requiring a click
            displayArtifact(data.file_path);
            
            // Keep the clickable functionality for the file path
            filePathElem.onclick = function() {
                displayArtifact(data.file_path);
                addMessage(`Viewing chart in the artifact window.`, 'system');
            };
        })
        .catch(error => {
            // Hide loader and show error message
            loader.classList.add('hidden');
            responseData.classList.remove('hidden');
            
            // Update UI with error info
            statusElem.textContent = 'Error';
            filePathElem.textContent = 'N/A';
            filePathElem.onclick = null;
            
            // Add error message to chat
            addMessage(`### Error\n\n${error.message}\n\nPlease check your API server and try again.`, 'system');
        });
    }
    
    // Function to display artifact in the right panel
    function displayArtifact(filePath) {
        // Set iframe source to the file path
        artifactFrame.src = filePath;
        
        // Hide placeholder and show content
        artifactPlaceholder.classList.add('hidden');
        artifactContent.classList.remove('hidden');
    }
    
    // Function to extract filename from path
    function extractFilename(path) {
        return path.split('/').pop();
    }
    
    // Function to format markdown properly
    function formatMarkdown(text) {
        // This function can be expanded to handle different markdown elements
        return text;
    }
    
    // Function to add a message to the chat
    function addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type);
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        
        // Parse markdown content
        if (type === 'system' && content.includes('#')) {
            // Simple markdown parser for headings, bold, italics, lists, etc.
            const parsedContent = content
                // Headers
                .replace(/### (.*)/g, '<h3>$1</h3>')
                .replace(/## (.*)/g, '<h2>$1</h2>')
                .replace(/# (.*)/g, '<h1>$1</h1>')
                // Bold
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                // Italic
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                // Lists
                .replace(/^\- (.*)/gm, '<li>$1</li>')
                // Line breaks
                .replace(/\n/g, '<br>');
                
            messageContent.innerHTML = parsedContent;
        } else {
            // Convert newlines to <br> tags for non-markdown content
            messageContent.innerHTML = content.replace(/\n/g, '<br>');
        }
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});