import io
import git
import math
#import yaml
import base64
import pathlib
import requests
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from collections import namedtuple
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
def get_CASTS_data_repo():
    """Clones the data catalogue"""
    try:
        git.Git(".").clone("https://github.com/NBStephens/streamlit-example.git")
    except git.GitCommandError:
        repo = git.Repo("apd-core")
        repo.remotes.origin.pull()


#@st.cache(suppress_st_warning=True)
def get_datasets_and_file_names() -> Dict:
    """Returns a dictionary of categories and files

    Returns
    -------
    Dict
        Key is the name of the category, value is a dictionary with information on files in that \
        category
    """
    path = pathlib.Path("Data")
    data_files = {}
    for i in path.glob("*.csv"):
        #st.write(i)
        file = str(i.parts[-1])
        data_files.update({str(file).replace(".csv", ""): file})
    return data_files


def broken_funciton():
        with file.open() as open_file:
            open_file_content = open_file.read()
            for old, new in CORRECTIONS.items():
                open_file_content = open_file_content.replace(old, new)
            #data_info = yaml.load(open_file_content, Loader=yaml.FullLoader)

        #if category in category_files:
            #category_files[category][file_name] = data_info
        #else:
         #   category_files[category] = {file_name: data_info}
    #except UnicodeDecodeError as err:
     #   category_files[category][file_name] = "NOT READABLE"
        # logging.exception("Error. Could not read %s", file.name, exc_info=err)

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
    path = pathlib.Path("apd-core/core") / category / file_name

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


def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    Adapted from:
    https://discuss.streamlit.io/t/heres-a-download-function-that-works-for-dataframes-and-txt/4052

    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

###Begin of main application


def main():
    get_CASTS_data_repo()

    data_dict = get_datasets_and_file_names()

    csv_list = [k for k, v in data_dict.items()]

    st.sidebar.image([morpho_logo, psu_logo], width=130, caption=["Duke University", "FEMR Lab"], output_format="PNG")
    """
    # Welcome to CSATS Morphosource Workshop! :skull:

    """
    with st.beta_expander("If you have any questions, please reach out:", expanded=True):
        """ 

        Slack Chat:speech_balloon: : [CSATS](https://app.slack.com/client/T9HGD7NBY/CTN0FTQCA)\n
        Email :email: : [Tim Ryan] (tmr21@psu.edu)\n
        Email :email: : [Nick stephens] (nbs49@psu.edu)\n    

        """



    col1, col2 = st.beta_columns(2)
    # Writes out a thing line across the gui page.


    with col1:
        st.write("---")
        slack_link = r"https://user-images.githubusercontent.com/819186/51553744-4130b580-1e7c-11e9-889e-486937b69475.png"

        option = st.selectbox('Select dataset', csv_list, key=9990237)

        st.write('You selected:', option)

        # Have to put ?raw=True at end to get the data

        brain_data = "https://github.com/NBStephens/streamlit-example/blob/master/Data/Powell%20Data%20-%20BrainSize%20vs%20BodySize.csv?raw=true"
        brain_paper = "https://github.com/NBStephens/streamlit-example/blob/master/Data/Powell%20et%20al.%2C%202017.pdfraw=truu"


        current_df = pd.read_csv(f"Data/{data_dict[option]}")
        current_pdf = brain_paper


        with st.beta_expander("View current dataset", expanded=True):
            st.write(current_df)
            if st.button('Download dataset as a CSV'):
                tmp_download_link = download_link(current_df,
                                                  download_filename=f'{str(option)}.csv',
                                                  download_link_text=f'Click here to download {str(option)} data!')
                st.markdown(tmp_download_link, unsafe_allow_html=True)



    with col2:
        title = st.empty()
        option = st.selectbox('Select a display type?',
                              ('Box plots', 'Scatter plots', 'Pie charts', 'Aleph viewer'))

        st.write('You selected:', option)
        if str(option) == "Aleph viewer":
            aleph_view_height = st.slider("Viewer height", min_value=1, max_value=1080, value=47)
            components.iframe("https://aleph-viewer.com/", height=int(aleph_view_height))
        #elif str(option) == "Box plots":


    col1_lower, col2_lower = st.beta_columns(2)
    with col1_lower:
        with st.beta_expander("Upload PDF"):
            pdf_file = st.file_uploader("", type=['pdf'])
        if pdf_file:
            with st.beta_expander("View or hide PDF"):
                pdf_view_size_ratio = st.slider("PDF viewer size", min_value=1, max_value=100, value=47)
                pdf_width = int(np.ceil(1920 * (pdf_view_size_ratio / 100)))
                pdf_height = int(np.ceil(pdf_width / 0.77))
                base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
                pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width={pdf_width} height={pdf_height} type="application/pdf">'
                st.markdown(pdf_display,
                            unsafe_allow_html=True)


    with col2_lower:
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