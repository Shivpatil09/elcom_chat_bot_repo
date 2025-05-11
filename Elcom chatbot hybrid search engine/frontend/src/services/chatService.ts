import axios, { AxiosError } from 'axios';

const RASA_ENDPOINT = 'http://localhost:5005/webhooks/rest/webhook';

export const sendMessage = async (message: string) => {
  try {
    console.log('Sending message to Rasa:', message);
    const response = await axios.post(RASA_ENDPOINT, {
      sender: 'user',
      message: message
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    
    console.log('Received response from Rasa:', response.data);
    
    // Rasa returns an array of messages
    if (Array.isArray(response.data) && response.data.length > 0) {
      return response.data;
    } else {
      console.warn('Received empty or invalid response from Rasa:', response.data);
      return [{ text: 'No results found. Please try a different search.' }];
    }
  } catch (error) {
    const axiosError = error as AxiosError;
    console.error('Error details:', {
      message: axiosError.message,
      response: axiosError.response?.data,
      status: axiosError.response?.status,
      headers: axiosError.response?.headers,
    });
    
    if (axiosError.code === 'ERR_NETWORK') {
      throw new Error('Cannot connect to the chatbot server. Please make sure it is running.');
    }
    
    throw axiosError;
  }
};