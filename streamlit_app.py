import io
import git
import math
#import yaml
import requests
import pandas as pd
import altair as alt
import streamlit as st
from collections import namedtuple
from pathlib import Path
from PIL import Image
from typing import Dict, Tuple, Union


morpho_logo = "https://www.morphosource.org/themes/morphosource/graphics/morphosource/morphosourceLogo.png"
psu_logo = "https://www.underconsideration.com/brandnew/archives/penn_state_logo_detail.png"
tim_pic = "https://sites.psu.edu/wisermurefurp/files/2020/08/Ryan.jpg"

st.set_page_config(page_title="CSATS Morphosource workshop",
                        page_icon=tim_pic,
                        layout='wide',
                        initial_sidebar_state='auto')

CORRECTIONS = {
    "DOI: ": "DOI ",
    "see: ": "see ",
    "from: ": "from ",
    "tables: ": "tables ",
    "1981â€“2016": "1981-2016",
}

@st.cache
def get_awesome_data_repo():
    """Clones the data catalogue"""
    try:
        git.Git(".").clone("https://github.com/awesomedata/apd-core")
    except git.GitCommandError:
        repo = git.Repo("apd-core")
        repo.remotes.origin.pull()


@st.cache
def get_categories_and_file_names() -> Dict:
    """Returns a dictionary of categories and files

    Returns
    -------
    Dict
        Key is the name of the category, value is a dictionary with information on files in that \
        category
    """
    path = Path("apd-core/core")
    category_files: Dict = {}
    for i in path.glob("**/*"):
        if i.is_dir():
            continue

        category, file_name = i.parts[-2:]

        file = Path("apd-core/core") / category / file_name
        # print(file)
        try:
            with file.open() as open_file:
                open_file_content = open_file.read()
                for old, new in CORRECTIONS.items():
                    open_file_content = open_file_content.replace(old, new)
                data_info = yaml.load(open_file_content, Loader=yaml.FullLoader)

            if category in category_files:
                category_files[category][file_name] = data_info
            else:
                category_files[category] = {file_name: data_info}
        except UnicodeDecodeError as err:
            category_files[category][file_name] = "NOT READABLE"
            # logging.exception("Error. Could not read %s", file.name, exc_info=err)

    return category_files


def get_data_info(category: str, file_name: str) -> Dict:
    """Returns a dictionary of information on the specified file

    Parameters
    ----------
    category : str
        The name of the category, like 'Sports'
    file_name : str
        A name of a file

    Returns
    -------
    Dict
        Information on the file
    """
    path = Path("apd-core/core") / category / file_name

    with path.open() as open_file:
        data = yaml.load(open_file.read(), Loader=yaml.FullLoader)
    return data


def create_info_table(selected_data_info: Dict):
    """Writes the information to the table

    Parameters
    ----------
    selected_data_info : Dict
        The information to show
    """
    info_table = pd.DataFrame()

    data_description = selected_data_info["description"]
    if data_description:
        line = pd.Series(data_description)
        line.name = "Description"
        info_table = info_table.append(line)

    keywords = selected_data_info["keywords"]
    if keywords:
        keywords = ", ".join(keywords.lower().split(","))
        line = pd.Series(keywords)
        line.name = "Keywords"
        info_table = info_table.append(line)

    if len(info_table) > 0:
        info_table.columns = [""]
        st.table(info_table)


@st.cache()
def check_url(url: str) -> Tuple[bool, Union[str, requests.Response]]:
    """Returns information on the availability of the url

    Parameters
    ----------
    url : str
        The url to test

    Returns
    -------
    Tuple[bool, Union[str, Response]]
        Whether the url is available and a string reponse
    """
    try:
        response = requests.head(url, allow_redirects=False)
        return True, response
    except requests.exceptions.SSLError:
        return False, "SSL error"
    except requests.exceptions.ConnectionError:
        return False, "Connection error"
    except requests.exceptions.InvalidSchema:
        return False, "Invalid schema"
    except requests.exceptions.MissingSchema:
        return check_url("https://" + url)


def show_homepage(data_info):
    """Shows information on the availability of the url to the user"""
    homepage = data_info["homepage"]

    if homepage.startswith("http:"):
        homepage = homepage.replace("http:", "https:")

    url_status, response = check_url(homepage)

    if url_status:
        if response.status_code in [301, 302]:
            st.info(f"{homepage}\n\nRedirects to {response.headers['Location']}")
        else:
            st.success(f"{homepage}")
    else:
        if response == "Connection error":
            st.error(f"{homepage}\n\nThere is a connection issue to this website.")
        elif response == "SSL error":
            st.warning(f"There might be an SSL issue with {homepage}\n\nProceed with caution!")
        else:
            st.info(f"{homepage}")


import base64

def main():
    st.sidebar.image([morpho_logo, psu_logo], width=130, caption=["Duke University", "FEMR Lab"], output_format="PNG")
    """
    # Welcome to CSATS Morphosource Workshop! :skull:

    """

    col1, col2 = st.beta_columns(2)
    # Writes out a thing line across the gui page.

    with col1:
        st.write("---")
        slack_link = r"https://user-images.githubusercontent.com/819186/51553744-4130b580-1e7c-11e9-889e-486937b69475.png"



        with st.beta_expander("If you have any questions, please reach out:", expanded=True):
            """ 
            
            Slack Chat:speech_balloon: : [CSATS](https://app.slack.com/client/T9HGD7NBY/CTN0FTQCA)\n
            Email :email: : [Tim Ryan] (tmr21@psu.edu)\n
            Email :email: : [Nick stephens] (nbs49@psu.edu)\n    
        
            """

        # Have to put ?raw=True at end to get the data
        brain_data = "https://github.com/NBStephens/streamlit-example/blob/master/Data/Powell%20Data%20-%20BrainSize%20vs%20BodySize.csv?raw=true"
        # brain_data = "https://drive.google.com/file/d/1A0QMMa7riZHTXwLid_YITPSKc7y-PpLt/view?usp=sharing?raw=tru"

        current_df = pd.read_csv(brain_data)
        with st.beta_expander("View current dataset", expanded=True):
            st.write(current_df)

    title = st.empty()

    st.sidebar.title("About")
    st.sidebar.info(
        "This app helps students visualizes scientific data to explore our evolutionary history"
        "\n\n"
        "It is maintained by [Nick Stephens](https://github.com/NBStephens/). "
        "If you have any technical issues please email nbs49@psu.edu"
    )

main()

with st.beta_expander(label="", expanded=False):
    '''
    
    #get_awesome_data_repo()
    
    categories_and_files = get_categories_and_file_names()
    
    category_file_count = {k: f"{k} ({len(v)})" for k, v in categories_and_files.items()}
    selected_topic = st.sidebar.selectbox(
        "Select topic",
        options=sorted(categories_and_files.keys()),
        format_func=category_file_count.get,
    )
    
    category_data = categories_and_files[selected_topic]
    
    data_titles = {k: v.get("title") for k, v in category_data.items()}
    
    selected_data = st.sidebar.selectbox(
        "Select data", options=sorted(category_data.keys()), format_func=data_titles.get
    )
    
    show_data_count_by_topic = st.sidebar.checkbox("Show data count by topic", value=True)
    
    selected_data_info = category_data[selected_data]
    
    title.title(selected_data_info["title"])
    data_image = selected_data_info.get("image", None)
    if data_image and data_image != "none":
        st.image(data_image, width=200)
    
    create_info_table(selected_data_info)
    
    show_homepage(selected_data_info)
    
    if show_data_count_by_topic:
        st.title(body="Data count by topic")
        source = pd.DataFrame(
            {
                "Topic": list(categories_and_files.keys()),
                "Number of data": [len(i) for i in categories_and_files.values()],
            }
        )
    
        chart = (
            alt.Chart(source)
            .mark_bar()
            .encode(alt.Y("Topic", title=""), alt.X("Number of data", title=""))
            .properties(height=600)
        )
    
        text = chart.mark_text(align="left", baseline="middle", dx=3).encode(text="Number of data")
    
        st.altair_chart(chart + text)
    '''