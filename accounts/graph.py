import matplotlib.pyplot as plt
import base64
from io import BytesIO

def Output_Graph():
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img = buffer.getvalue()
    graph = base64.b64encode(img)
    graph = graph.decode("utf-8")
    buffer.close()
    return graph

def Plot_Graph(x,y):
    plt.switch_backend("AGG")
    plt.figure(figsize=(10,5))
    plt.bar(x,y)
    plt.xticks(rotation=45)
    plt.yticks([i for i in range(max(y) + 1)])
    plt.ylabel("冊", fontname="Yu Gothic", fontsize=12, color='gray', labelpad=10)
    plt.tight_layout()
    graph = Output_Graph()
    return graph