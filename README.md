Document Parser for Specific info. Uses OpenAI api to search for themes, topics, ideas in documents and then exports organized .csv reports which can easily be compiled into a database for analysis. 



To run: 1) add your own API key to the .env 
2) set your own directory
3) Use Indiv.py

To do a custom parse just find and customize the prompt and response in this section below:

    prompt = f"Search the following text for references of virtual reality, augmented reality, and mixed reality headsets and associated software names:\n\n{chunk}\n\nProvide a list of device names and a list of software names separately, along with the relevant excerpts, focusing only on the hardware and software used in studies from {current_year} or later. Exclude any references to studies published before {current_year}."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": f"You are an AI assistant that specializes in identifying and listing virtual reality, augmented reality, and mixed reality headsets and associated software names mentioned in a given text, focusing only on studies from {current_year} or later."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7,
        )
