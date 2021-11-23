# contentstack-data-migrator
An extended content migrator utility across stacks and accounts for contentstack headless CMS


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#references">References</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This utility automates the process of manual syncing of contents from one stack’s environment to another environment in another stack in contentstack. This utility uses Management API’s and Delivery API’s to make these automations. For information about these apis visit [here](https://www.contentstack.com/docs/developers/apis/content-management-api/) and [here](https://www.contentstack.com/docs/developers/apis/content-delivery-api/).


### Built With

* [Python](https://www.python.org/)


<!-- GETTING STARTED -->
## Getting Started

To get a local copy of the utilty up and running follow these steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* python <br /> Python can be installed by following standard installation available at [python.org](https://www.python.org/) or can also installed through [Anaconda](https://www.anaconda.com/)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/DeepakDP5/contentstack-push-to-prod.git
   ```
2. Install Requirements
   ```sh
   pip install -r requirements.txt
   ```

### Setup
* Configure config.py file
  - Base URLs for contentstack APIs
  - Required access tokens and api_keys

<!-- USAGE EXAMPLES -->
## Usage

How to use:
1.  To automate everything. <br />
    Run command 
      ```sh
      python main.py A -u B -d C
      ```
    where A, B, and C are:
    *  A - all/assets/content_types/entries that the user wants to sync.(preferably use ‘all’ as an argument)
    *  B - username(to be displayed in log file)
    *  C - date(YYYY-MM-DD) after which syncing needs to start.
    *  -l/--list_only is optional. If this argument is provided only a list of all updates that needs to be made will be shown.
  
    Example:
    ```sh
    python main.py all -u user_name -d 2021-07-01 -l
    ```

2.  To perform atomic updates.<br />
    * For assets and content types:
      Run command 
      ```sh
      python main.py A -u B --uid C
      ```
      * A - asset/content_type that the user wants to sync.
      * B - username(to be displayed in log file)
      * C - uid value of asset or content type that needs to be synced. Use ‘uid’ argument multiple times if multiple assets/content_type needs to be created/updated.
      Example:
      ```sh
      python main.py -u user_name asset --uid blta4998ba0ce2321a6 --uid blt518edaf6c6355
      ```
    * For entry:
      Run command 
      ```sh
      python main.py A -u B --uid C --ct D
      ```
      * A - entry
      * B - username(to be displayed in log file)
      * C - uid value of entry that needs to be synced.
      * D - corresponding content type uid. Use ‘--uid C --ct D’ multiple times if more than one entry needs to be created/updated.
      Example:
      ```sh
      python main.py -u user_name entry --uid blt9bcd123ced793cf3 --ct footer --uid blta84178567c5a7c1b --ct header
      ```

3.  Run following command to view help.
    ```sh
    python main.py -h
    ```

<!-- CONTACT -->
## Contact
Arun Paliwal - arun.paliwal@publicissapient.com

Deepak Patil - deepak.patil@publicissapient.com

Akash Patel - akash.patel@publicissapient.com

Project Link: [https://github.com/DeepakDP5/contentstack-push-to-prod](https://github.com/DeepakDP5/contentstack-push-to-prod)



<!-- REFERENCES -->
## References

* [Contentstack Delivery APIs](https://www.contentstack.com/docs/developers/apis/content-delivery-api/)
* [Contentstack Management APIs](https://www.contentstack.com/docs/developers/apis/content-management-api/)
