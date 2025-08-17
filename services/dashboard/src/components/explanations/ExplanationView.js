import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import SHAPChart from "./SHAPChart";
import GraphVisualization from "./GraphVisualization";
import { useApi } from "../../hooks/useApi";
