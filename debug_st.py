import streamlit as st
import sys

print(f"Python version: {sys.version}")
print(f"Streamlit version: {st.__version__}")

try:
    print(f"Has st.dialog: {st.dialog}")
except AttributeError:
    print("Does NOT have st.dialog")

try:
    print(f"Has st.experimental_dialog: {st.experimental_dialog}")
except AttributeError:
    print("Does NOT have st.experimental_dialog")
