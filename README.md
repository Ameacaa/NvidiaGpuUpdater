## Nvidia GPU Updater
Download the latest GPU driver without relying on GeForce Experience. 

#### Why I don't like Geforce Experience:
- Resource Consumption: GeForce Experience runs in the background and consumes CPU and memory unnecessarely.
- Bloatware: Unnecessary software. You don't need it to have the latest driver version.
- Privacy: Need account, why? And it collects some data about the system and game habits, maybe more.

#### Requirements:
- Selenium Chrome (May change in future updates due to overkill solution, it's too much for a project like this, take too much time, ressources and possible problems)

#### How It Works:
1. Opens the NVIDIA drivers page and selects your GPU using dropdown menus.
2. Clicks "Search" to find the available drivers.
3. Compares the available driver version with your current driver version.
4. Downloads the latest driver if one is available.

#### Future Updates (Desired):
- Explore alternative methods to Selenium for improved efficiency and reliability.
- Implement a more user-friendly method for selecting your GPU.
